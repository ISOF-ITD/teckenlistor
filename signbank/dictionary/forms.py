# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist

from tagging.models import Tag

from .models import build_choice_list
from .models import Dataset, Language, SignLanguage, AllowedTags, GlossRelation, Gloss, Relation, \
    RelationToForeignSign, MorphologyDefinition,  FieldChoice, GlossURL


class GlossCreateForm(forms.ModelForm):
    """
    Form for creating a new gloss.
    This form also overrides the ModelForm validations.
    """
    attrs_reqd_focus = {'class': 'form-control', 'autofocus': '', 'required': ''}
    attrs_default = {'class': 'form-control'}
    # TODO: Check dataset permissions
    dataset = forms.ModelChoiceField(label=_('Dataset'), required=True, queryset=Dataset.objects.all(), empty_label=None)

    idgloss = forms.CharField(label=_('Gloss'), required=True, widget=forms.TextInput(attrs=attrs_reqd_focus))
    idgloss_en = forms.CharField(label=_('Gloss in English'), required=False,
                                 widget=forms.TextInput(attrs=attrs_default))
    videofile = forms.FileField(label=_('Gloss video'), allow_empty_file=True, required=False)
    video_title = forms.CharField(label=_('Glossvideo title'), required=False)

    try:
        qs = AllowedTags.objects.get(content_type=ContentType.objects.get_for_model(Gloss)).allowed_tags.all()
    except ObjectDoesNotExist:
        qs = Tag.objects.all()
    tag = forms.ModelChoiceField(queryset=qs, required=False, empty_label="---", to_field_name='name',
                                 widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Gloss
        fields = ['dataset', 'idgloss', 'idgloss_en', 'videofile']

    def clean(self):
        """
        Validate the form data.
        """
        pass # Nothing here at the moment.

    def clean_idgloss(self):
        """
        Validates that the idgloss value in the chosen Dataset has not been taken yet.

        """
        try:
            gloss = Gloss.objects.get(idgloss__exact=self.cleaned_data['idgloss'], dataset=self.cleaned_data['dataset'])
        except Gloss.DoesNotExist:
            return self.cleaned_data['idgloss']
        raise forms.ValidationError(
            # Translators: exception ValidationError
            _('This Gloss value already exists in the chosen Dataset. Please choose another value for Gloss.'),
            code='not_unique')

    def clean_idgloss_en(self):
        """
        Overrides the default validations for idgloss_en.
        Currently we don't want to validate this field.

        """
        return self.cleaned_data['idgloss_en']

    def clean_videofile(self):
        # Checking here that the file ends with .mp4 TODO: See if more checks are needed, like filetype, codec
        if self.cleaned_data['videofile'] and not self.cleaned_data['videofile'].name.endswith('.mp4'):
            raise forms.ValidationError('File is not a mp4. Please upload only mp4 files')
        return self.cleaned_data['videofile']

    def clean_video_title(self):
        return self.cleaned_data['video_title']


class TagUpdateForm(forms.Form):
    """Form to add a new tag to a gloss"""
    try:
        qs = AllowedTags.objects.get(content_type=ContentType.objects.get_for_model(Gloss)).allowed_tags.all()
    except ObjectDoesNotExist:
        qs = Tag.objects.all()
    tag = forms.ModelChoiceField(queryset=qs, empty_label=None, to_field_name='name',
                                 widget=forms.Select(attrs={'class': 'form-control'}))
    delete = forms.BooleanField(required=False, widget=forms.HiddenInput)


class TagsAddForm(forms.Form):
    """Form to add a new tags to a gloss"""
    try:
        qs = AllowedTags.objects.get(content_type=ContentType.objects.get_for_model(Gloss)).allowed_tags.all()
    except ObjectDoesNotExist:
        qs = Tag.objects.all()
    tags = forms.ModelMultipleChoiceField(label=_('Tags'), queryset=qs, to_field_name='name')


NULLBOOLEANCHOICES = [
    (0, '---------'),
    # Translators: YESNOCHOICES
    (1, _('Unknown')),
    # Translators: YESNOCHOICES
    (2, _('True')),
    # Translators: YESNOCHOICES
    (3, _('False'))]

RELATION_ROLE_CHOICES = (('', '---------'),
                         # Translators: RELATION_ROLE_CHOICES
                         ('all', _('All')),
                         # Translators: RELATION_ROLE_CHOICES
                         ('homonym', _('Homonym')),
                         # Translators: RELATION_ROLE_CHOICES
                         ('synonym', _('Synonym')),
                         # Translators: RELATION_ROLE_CHOICES
                         ('variant', _('Variant')),
                         # Translators: RELATION_ROLE_CHOICES
                         ('antonym', _('Antonym')),
                         # Translators: RELATION_ROLE_CHOICES
                         ('hyponym', _('Hyponym')),
                         # Translators: RELATION_ROLE_CHOICES
                         ('hypernym', _('Hypernym')),
                         # Translators: RELATION_ROLE_CHOICES
                         ('seealso', _('See Also')),
                         )

MORPHEME_ROLE_CHOICES = [
                            # Translators: This is a choice option that probably represents nothing, don't translate if not needed to.
                            ('', _('---------'))] + build_choice_list('MorphologyType')
ATTRS_FOR_FORMS = {'class': 'form-control'}


class GlossSearchForm(forms.ModelForm):
    # Translators: GlossSearchForm label
    dataset = forms.ModelMultipleChoiceField(label=_('Dataset'), queryset=Dataset.objects.all(), required=False)
    # Translators: GlossSearchForm label
    signlanguage = forms.ModelMultipleChoiceField(label=_('Sign language'), queryset=SignLanguage.objects.all(),
                                                  required=False)

    search = forms.CharField(label=_("Search"))
    # Translators: GlossSearchForm label
    gloss = forms.CharField(label=_("Gloss"))
    # Translators: GlossSearchForm label
    idgloss_en = forms.CharField(label=_("Gloss in English"))
    # Translators: GlossSearchForm label
    keyword = forms.CharField(label=_('Translations'))
    # Translators: GlossSearchForm label
    trans_lang = forms.ModelChoiceField(required=False, empty_label=_('Choose language'), queryset=Language.objects.all())

    try:
        qs = AllowedTags.objects.get(content_type=ContentType.objects.get_for_model(Gloss)).allowed_tags.all()
    except ObjectDoesNotExist:
        qs = Tag.objects.all()
    tags = forms.ModelMultipleChoiceField(queryset=qs, required=False)
    nottags = forms.ModelMultipleChoiceField(queryset=qs)

    published = forms.BooleanField(label=_('Gloss is published'), required=False)

    # Translators: GlossSearchForm label
    hasvideo = forms.BooleanField(label=_('Gloss has a video'), required=False)
    hasnovideo = forms.BooleanField(label=_('Gloss does not have a video'), required=False)

    # These have been disabled until they are later needed
    # TODO: To enable these, uncomment them.
    """
    # Translators: GlossSearchForm label
    relation = forms.CharField(
        label=_('Search for gloss of related signs'), widget=forms.TextInput(attrs=ATTRS_FOR_FORMS))
    # Translators: GlossSearchForm label
    relationToForeignSign = forms.CharField(
        label=_('Search for gloss of foreign signs'), widget=forms.TextInput(attrs=ATTRS_FOR_FORMS))
    # Translators: GlossSearchForm label
    morpheme = forms.CharField(
        label=_('Search for gloss with this as morpheme'), widget=forms.TextInput(attrs=ATTRS_FOR_FORMS))

    # Translators: GlossSearchForm label
    phonology_other = forms.CharField(
        label=_('Phonology other'), widget=forms.TextInput())

    # Translators: GlossSearchForm label
    hasRelationToForeignSign = forms.ChoiceField(label=_('Related to foreign sign or not'), choices=[
        (0, '---------'), (1, _('Yes')), (2, _('No'))], widget=forms.Select(attrs=ATTRS_FOR_FORMS))
    # Translators: GlossSearchForm label
    hasRelation = forms.ChoiceField(
        label=_('Type of relation'), choices=RELATION_ROLE_CHOICES, widget=forms.Select(attrs=ATTRS_FOR_FORMS))
    # Translators: GlossSearchForm label
    hasMorphemeOfType = forms.ChoiceField(
        label=_('Has morpheme type'), choices=MORPHEME_ROLE_CHOICES, widget=forms.Select(attrs=ATTRS_FOR_FORMS))

    # Translators: GlossSearchForm label
    repeated_movement = forms.ChoiceField(
        label=_('Repeating Movement'), choices=NULLBOOLEANCHOICES)
    # ,widget=forms.Select(attrs=ATTRS_FOR_FORMS));
    # Translators: GlossSearchForm label
    alternating_movement = forms.ChoiceField(
        label=_('Alternating Movement'), choices=NULLBOOLEANCHOICES)
    """

    class Meta:
        ATTRS_FOR_FORMS = {'class': 'form-control'}

        model = Gloss
        fields = ('idgloss', 'idgloss_en', 'dialect', 'strong_handshape', 'weak_handshape', 'location',
                  'handedness', 'notes', 'relation_between_articulators', 'absolute_orientation_palm',
                  'absolute_orientation_fingers', 'relative_orientation_movement', 'relative_orientation_location',
                  'orientation_change', 'handshape_change', 'repeated_movement', 'alternating_movement',
                  'movement_shape', 'movement_direction', 'movement_manner', 'contact_type', 'mouth_gesture',
                  'mouthing', 'phonetic_variation', 'iconic_image', 'named_entity', 'semantic_field',
                  'number_of_occurences',)


class GlossRelationForm(forms.Form):
    source = forms.CharField(widget=forms.HiddenInput())
    target = forms.CharField(label=_("Gloss"), widget=forms.TextInput(attrs={'class': 'glossrelation-autocomplete'}))
    try:
        qs = AllowedTags.objects.get(content_type=ContentType.objects.get_for_model(GlossRelation)).allowed_tags.all()
    except ObjectDoesNotExist:
        qs = Tag.objects.all()
    tag = forms.ModelChoiceField(label=_("Relation type:"),
                                 queryset=qs,
                                 required=True, to_field_name='name',
                                 widget=forms.Select(attrs={'class': 'form-control'}))
    delete = forms.IntegerField(required=False, widget=forms.HiddenInput())


class GlossURLForm(forms.ModelForm):
    class Meta:
        model = GlossURL
        fields = ["gloss", "url"]


class RelationForm(forms.ModelForm):
    # Translators: RelationForm label
    sourceid = forms.CharField(label=_('Source Gloss'))
    # Translators: RelationForm label
    targetid = forms.CharField(label=_('Target Gloss'))
    # Note that to_field_name has to be unique!
    role = forms.ModelChoiceField(label=_('Type'), queryset=FieldChoice.objects.filter(field='MorphologyType'),
                                  to_field_name='machine_value', empty_label=None,
                                  widget=forms.Select(attrs=ATTRS_FOR_FORMS))

    class Meta:
        model = Relation
        fields = ['role']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-control'}),
        }


class RelationToForeignSignForm(forms.ModelForm):
    # Translators: RelationToForeignSignForm label
    sourceid = forms.CharField(label=_('Source Gloss'))
    # loan = forms.CharField(label='Loan')
    # Translators: RelationToForeignSignForm label
    other_lang = forms.CharField(label=_('Related Language'))
    # Translators: RelationToForeignSignForm label
    other_lang_gloss = forms.CharField(label=_('Gloss in Related Language'))

    class Meta:
        model = RelationToForeignSign
        fields = ['loan', 'other_lang', 'other_lang_gloss']
        widgets = {}


class MorphologyForm(forms.ModelForm):
    # Translators: MorphologyForm label
    parent_gloss_id = forms.CharField(label=_('Parent Gloss'))
    # role = forms.ChoiceField(label=_('Type'), choices=build_choice_list(
    #    'MorphologyType'), widget=forms.Select(attrs=ATTRS_FOR_FORMS))

    # Note that to_field_name has to be unique!
    role = forms.ModelChoiceField(label=_('Type'), queryset=FieldChoice.objects.filter(field='MorphologyType'),
                                  to_field_name='machine_value', empty_label=None,
                                  widget=forms.Select(attrs=ATTRS_FOR_FORMS))

    # role = forms.ChoiceField(label=_('Type'), widget=forms.Select(attrs=ATTRS_FOR_FORMS))
    # Translators: MorphologyForm label
    morpheme_id = forms.CharField(label=_('Morpheme'))

    class Meta:
        model = MorphologyDefinition
        fields = ['role']


class CSVUploadForm(forms.Form):
    file = forms.FileField()
    dataset = forms.ModelChoiceField(queryset=Dataset.objects.all(), empty_label=None)


class GlossPublicSearchForm(forms.Form):
    """Public search form."""
    search = forms.CharField(label=_("Search"), required=False,
                             widget=forms.TextInput(attrs={'placeholder': _('Search signs')}))
    dataset = forms.ModelMultipleChoiceField(queryset=Dataset.objects.filter(is_public=True), required=False,
                                             label=_("Lexicon"), widget=forms.CheckboxSelectMultiple(),
                                             help_text=_("You can limit the search to these lexicons."))
