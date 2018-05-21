# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.db.models import Q, Prefetch
from django.utils.translation import get_language
from django.db.models.functions import Substr, Upper

from .models import Gloss, Translation, GlossTranslations, SignLanguage, Dataset, GlossRelation
# ISOF Per
from tagging.models import Tag, TaggedItem

from ..video.models import GlossVideo
from .forms import GlossPublicSearchForm
from .adminviews import populate_tags_for_object_list

# autocomplete
# from dal import autocomplete
from django.views.generic.edit import FormView
import json
from django.http import HttpResponse

def applicationRoot(request):
    if request is not None:
        paths = request.get_full_path().split('/')
        application_root = ''
        if paths[1] == 'teckenlistor':
            application_root = paths[1]
            # application_root = '/teckenlistor'
            # environment_url = paths[2:]
    return application_root

# Only test
# class GlossAutocomplete(autocomplete.Select2QuerySetView):
#     def get_queryset(self):
#         # Don't forget to filter out results depending on the visitor !
#         if not self.request.user.is_authenticated():
#             return Gloss.objects.none()
#
#         qs = Gloss.objects.all()
#
#         if self.q:
#             qs = qs.filter(idgloss__istartswith=self.q)
#
#         return qs

# *code in view which returns json data *
class GlossAutoCompleteView(FormView):
    def get(self,request,*args,**kwargs):
        data = request.GET
        name = data.get("term")
        if name:
            glosses = Gloss.objects.filter(idgloss__istartswith = name)
        else:
            glosses = Gloss.objects.all()
        results = []
        for gloss in glosses:
            all_json = {}
            all_json['id'] = gloss.id
            all_json['label'] = gloss.idgloss
            all_json['value'] = gloss.idgloss
            results.append(all_json)
        data = json.dumps(results)
        mimetype = 'application/json'
        return HttpResponse(data, mimetype)


class GlossListPublicTagsVideoView(ListView):
    model = Gloss
    template_name = 'dictionary/public_gloss_list_tagsvideo.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(GlossListPublicTagsVideoView, self).get_context_data(**kwargs)
        context["searchform"] = GlossPublicSearchForm(self.request.GET)
        context["signlanguages"] = SignLanguage.objects.filter(id__in=[x.signlanguage.id for x in Dataset.objects.filter(is_public=True)])
        context["lang"] = self.request.GET.get("lang")
        if context["lang"]:
            context["searchform"].fields["dataset"].queryset = context["searchform"].fields["dataset"].queryset.filter(signlanguage__language_code_3char=context["lang"])
        context["first_letters"] = Gloss.objects.filter(dataset__is_public=True, published=True)\
            .annotate(first_letters=Substr(Upper('idgloss'), 1, 1)).order_by('first_letters')\
            .values_list('first_letters').distinct()

        # ISOF Per
        # tags_list = Tag.objects.filter(approved=0).order_by('-date')[:30]
        tag_list = Tag.objects.all()
        context["tags"] = tag_list
        # application_root = applicationRoot(self.request)
        # context["application_root"] = application_root
        # populate_tags_for_object_list(context['object_list'], model=self.object_list.model)

        # context['gloss_choices'] = Gloss.objects.filter(dataset=self.request.GET.get('dataset'))
        context['gloss_choices'] = Gloss.objects.all()

        return context

    def get_queryset(self):
        # Get queryset
        qs = super(GlossListPublicTagsVideoView, self).get_queryset()
        get = self.request.GET

        # Exclude datasets that are not public.
        qs = qs.exclude(dataset__is_public=False)
        # Exclude glosses that are not 'published'.
        qs = qs.exclude(published=False)

        if 'lang' in get and get['lang'] != '' and get['lang'] != 'all':
            signlang = get.get('lang')
            qs = qs.filter(dataset__signlanguage__language_code_3char=signlang)

        # Search for multiple datasets (if provided)
        vals = get.getlist('dataset', [])
        if vals != []:
            qs = qs.filter(dataset__in=vals)

        if 'search' in get and get['search'] != '':
            val = get['search']

            # ISOF test
            category = get.get('tags', 'Alla')

            # Filters
            qs = qs.filter(Q(idgloss__istartswith=val) | Q(translation__keyword__text__istartswith=val)
                           # | Q(idgloss_en__icontains=val) # idgloss_en not shown in results, therefore removed.
                           )

        # From class GlossListView(ListView) in adminviews.py
        if 'tags' in get and get['tags'] != '':
            vals = get.getlist('tags')

            tags = []
            for t in vals:
                tags.extend(Tag.objects.filter(pk=t))

            # search is an implicit AND so intersection
            tqs = TaggedItem.objects.get_intersection_by_model(Gloss, tags)

            # intersection
            qs = qs & tqs

            # print "J :", len(qs)


        qs = qs.distinct()

        # Set order according to GET field 'order'
        if 'order' in get:
            qs = qs.order_by(get['order'])
        else:
            qs = qs.order_by('idgloss')

        # Prefetching translation and dataset objects for glosses to minimize the amount of database queries.
        qs = qs.prefetch_related(Prefetch('translation_set', queryset=Translation.objects.filter(
            language__language_code_2char__iexact=get_language()).select_related('keyword')),
                                 Prefetch('glosstranslations_set', queryset=GlossTranslations.objects.filter(
                                     language__language_code_2char__iexact=get_language())),
                                 Prefetch('dataset'),
                                 # Ordering by version to get the first versions posterfile.
                                 Prefetch('glossvideo_set', queryset=GlossVideo.objects.all().order_by('version')))
        return qs


class GlossListPublicTagsView(ListView):
    model = Gloss
    template_name = 'dictionary/public_gloss_list_tags.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(GlossListPublicTagsView, self).get_context_data(**kwargs)
        context["searchform"] = GlossPublicSearchForm(self.request.GET)
        context["signlanguages"] = SignLanguage.objects.filter(id__in=[x.signlanguage.id for x in Dataset.objects.filter(is_public=True)])
        context["lang"] = self.request.GET.get("lang")
        if context["lang"]:
            context["searchform"].fields["dataset"].queryset = context["searchform"].fields["dataset"].queryset.filter(signlanguage__language_code_3char=context["lang"])
        context["first_letters"] = Gloss.objects.filter(dataset__is_public=True, published=True)\
            .annotate(first_letters=Substr(Upper('idgloss'), 1, 1)).order_by('first_letters')\
            .values_list('first_letters').distinct()

        # ISOF Per
        # tags_list = Tag.objects.filter(approved=0).order_by('-date')[:30]
        tag_list = Tag.objects.all()
        context["tags"] = tag_list
        # application_root = applicationRoot(self.request)
        # context["application_root"] = application_root
        # populate_tags_for_object_list(context['object_list'], model=self.object_list.model)

        # context['gloss_choices'] = Gloss.objects.filter(dataset=self.request.GET.get('dataset'))
        context['gloss_choices'] = Gloss.objects.all()

        return context

    def get_queryset(self):
        # Get queryset
        qs = super(GlossListPublicTagsView, self).get_queryset()
        get = self.request.GET

        # Exclude datasets that are not public.
        qs = qs.exclude(dataset__is_public=False)
        # Exclude glosses that are not 'published'.
        qs = qs.exclude(published=False)

        if 'lang' in get and get['lang'] != '' and get['lang'] != 'all':
            signlang = get.get('lang')
            qs = qs.filter(dataset__signlanguage__language_code_3char=signlang)

        # Search for multiple datasets (if provided)
        vals = get.getlist('dataset', [])
        if vals != []:
            qs = qs.filter(dataset__in=vals)

        if 'search' in get and get['search'] != '':
            val = get['search']

            # ISOF test
            category = get.get('tags', 'Alla')

            # Filters
            qs = qs.filter(Q(idgloss__istartswith=val) | Q(translation__keyword__text__istartswith=val)
                           # | Q(idgloss_en__icontains=val) # idgloss_en not shown in results, therefore removed.
                           )

        # From class GlossListView(ListView) in adminviews.py
        if 'tags' in get and get['tags'] != '':
            vals = get.getlist('tags')

            tags = []
            for t in vals:
                tags.extend(Tag.objects.filter(pk=t))

            # search is an implicit AND so intersection
            tqs = TaggedItem.objects.get_intersection_by_model(Gloss, tags)

            # intersection
            qs = qs & tqs

            # print "J :", len(qs)


        qs = qs.distinct()

        # Set order according to GET field 'order'
        if 'order' in get:
            qs = qs.order_by(get['order'])
        else:
            qs = qs.order_by('idgloss')

        # Prefetching translation and dataset objects for glosses to minimize the amount of database queries.
        qs = qs.prefetch_related(Prefetch('translation_set', queryset=Translation.objects.filter(
            language__language_code_2char__iexact=get_language()).select_related('keyword')),
                                 Prefetch('glosstranslations_set', queryset=GlossTranslations.objects.filter(
                                     language__language_code_2char__iexact=get_language())),
                                 Prefetch('dataset'),
                                 # Ordering by version to get the first versions posterfile.
                                 Prefetch('glossvideo_set', queryset=GlossVideo.objects.all().order_by('version')))
        return qs

class GlossListPublicView(ListView):
    model = Gloss
    template_name = 'dictionary/public_gloss_list.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(GlossListPublicView, self).get_context_data(**kwargs)
        context["searchform"] = GlossPublicSearchForm(self.request.GET)
        context["signlanguages"] = SignLanguage.objects.filter(id__in=[x.signlanguage.id for x in Dataset.objects.filter(is_public=True)])
        context["lang"] = self.request.GET.get("lang")
        if context["lang"]:
            context["searchform"].fields["dataset"].queryset = context["searchform"].fields["dataset"].queryset.filter(signlanguage__language_code_3char=context["lang"])
        context["first_letters"] = Gloss.objects.filter(dataset__is_public=True, published=True)\
            .annotate(first_letters=Substr(Upper('idgloss'), 1, 1)).order_by('first_letters')\
            .values_list('first_letters').distinct()
        return context

    def get_queryset(self):
        # Get queryset
        qs = super(GlossListPublicView, self).get_queryset()
        get = self.request.GET

        # Exclude datasets that are not public.
        qs = qs.exclude(dataset__is_public=False)
        # Exclude glosses that are not 'published'.
        qs = qs.exclude(published=False)

        if 'lang' in get and get['lang'] != '' and get['lang'] != 'all':
            signlang = get.get('lang')
            qs = qs.filter(dataset__signlanguage__language_code_3char=signlang)

        # Search for multiple datasets (if provided)
        vals = get.getlist('dataset', [])
        if vals != []:
            qs = qs.filter(dataset__in=vals)

        if 'search' in get and get['search'] != '':
            val = get['search']
            # Filters
            qs = qs.filter(Q(idgloss__istartswith=val) | Q(translation__keyword__text__istartswith=val)
                           # | Q(idgloss_en__icontains=val) # idgloss_en not shown in results, therefore removed.
                           )

        qs = qs.distinct()

        # Set order according to GET field 'order'
        if 'order' in get:
            qs = qs.order_by(get['order'])
        else:
            qs = qs.order_by('idgloss')

        # Prefetching translation and dataset objects for glosses to minimize the amount of database queries.
        qs = qs.prefetch_related(Prefetch('translation_set', queryset=Translation.objects.filter(
            language__language_code_2char__iexact=get_language()).select_related('keyword')),
                                 Prefetch('glosstranslations_set', queryset=GlossTranslations.objects.filter(
                                     language__language_code_2char__iexact=get_language())),
                                 Prefetch('dataset'),
                                 # Ordering by version to get the first versions posterfile.
                                 Prefetch('glossvideo_set', queryset=GlossVideo.objects.all().order_by('version')))
        return qs

class GlossDetailPublicView(DetailView):
    model = Gloss
    template_name = 'dictionary/public_gloss_detail.html'
    context_object_name = 'gloss'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(GlossDetailPublicView, self).get_context_data(**kwargs)
        context['translation_languages_and_translations'] = context['gloss'].get_translations_for_translation_languages()
        # GlossRelations for this gloss
        context['glossrelations'] = GlossRelation.objects.filter(source=context['gloss'])
        context['glossrelations_reverse'] = GlossRelation.objects.filter(target=context['gloss'])
        return context
