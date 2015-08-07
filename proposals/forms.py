from django import forms
from django.forms.models import inlineformset_factory
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from .models import Proposal, Wmo, Study, Session, Task

yes_no = [(True, _('ja')), (False, _('nee'))]
yes_no_doubt = [(True, _('ja')), (False, _('nee')), (None, _('twijfel'))]


class ProposalForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = ['relation', 'supervisor_email', 'other_applicants',
                  'applicants', 'title', 'tech_summary', 'longitudinal']
        widgets = {
            'relation': forms.RadioSelect(),
            'other_applicants': forms.RadioSelect(choices=yes_no),
            'longitudinal': forms.RadioSelect(choices=yes_no),
            'tech_summary': forms.Textarea(attrs={'rows': 30, 'cols': 80})
        }
        error_messages = {
            'title': {
                'unique': _('Er bestaat al een studie met deze titel.'),
            },
        }

    def __init__(self, *args, **kwargs):
        """Remove empty label from relation field"""
        super(ProposalForm, self).__init__(*args, **kwargs)
        self.fields['relation'].empty_label = None

    def clean(self):
        """
        Check for conditional requirements:
        - If relation needs supervisor, make sure supervisor_email is set
        - If other_applicants is checked, make sure applicants are set
        - Maximum number of words for tech_summary (TODO: magic number)
        """
        cleaned_data = super(ProposalForm, self).clean()
        relation = cleaned_data.get('relation')
        supervisor_email = cleaned_data.get('supervisor_email')
        other_applicants = cleaned_data.get('other_applicants')
        applicants = cleaned_data.get('applicants')
        tech_summary = cleaned_data.get('tech_summary')

        if relation and relation.needs_supervisor and not supervisor_email:
            error = forms.ValidationError(_('U dient een eindverantwoordelijke op te geven.'), code='required')
            self.add_error('supervisor_email', error)

        if other_applicants and len(applicants) == 1:
            error = forms.ValidationError(_('U heeft geen andere onderzoekers geselecteerd.'), code='required')
            self.add_error('applicants', error)

        if tech_summary and len(tech_summary.split()) > 600:
            error = forms.ValidationError(_('De samenvatting bestaat uit teveel woorden.'), code='max')
            self.add_error('tech_summary', error)


class ProposalCopyForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = ['parent']


class WmoForm(forms.ModelForm):
    class Meta:
        model = Wmo
        fields = ['metc', 'metc_institution', 'is_medical', 'is_behavioristic',
                  'metc_application', 'metc_decision', 'metc_decision_pdf']
        widgets = {
            'metc': forms.RadioSelect(choices=yes_no_doubt),
            'is_medical': forms.RadioSelect(choices=yes_no_doubt),
            'is_behavioristic': forms.RadioSelect(choices=yes_no_doubt),
            'metc_application': forms.RadioSelect(choices=yes_no),
            'metc_decision': forms.RadioSelect(choices=yes_no),
        }

    def clean(self):
        """
        Check for conditional requirements:
        - If metc is checked, make sure institution is set
        """
        cleaned_data = super(WmoForm, self).clean()
        metc = cleaned_data.get('metc')
        metc_institution = cleaned_data.get('metc_institution')

        if metc and not metc_institution:
            error = forms.ValidationError(_('U dient een instelling op te geven.'), code='required')
            self.add_error('metc_institution', error)


class StudyForm(forms.ModelForm):
    class Meta:
        model = Study
        fields = ['age_groups',
                  'has_traits', 'traits', 'traits_details',
                  'necessity', 'necessity_reason',
                  'setting', 'setting_details',
                  'risk_physical', 'risk_psychological',
                  'compensation', 'compensation_details',
                  'recruitment', 'recruitment_details']
        widgets = {
            'age_groups': forms.CheckboxSelectMultiple(),
            'has_traits': forms.RadioSelect(choices=yes_no),
            'traits': forms.CheckboxSelectMultiple(),
            'necessity': forms.RadioSelect(choices=yes_no_doubt),
            'risk_physical': forms.RadioSelect(choices=yes_no_doubt),
            'setting': forms.CheckboxSelectMultiple(),
            'risk_psychological': forms.RadioSelect(choices=yes_no_doubt),
            'compensation': forms.RadioSelect(),
            'recruitment': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        """Remove empty label from setting field"""
        super(StudyForm, self).__init__(*args, **kwargs)
        self.fields['setting'].empty_label = None
        self.fields['compensation'].empty_label = None


class SessionStartForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = ['sessions_number']

    def __init__(self, *args, **kwargs):
        """Set the sessions_number field as required"""
        super(SessionStartForm, self).__init__(*args, **kwargs)
        self.fields['sessions_number'].required = True


class TaskStartForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['tasks_number']

    def __init__(self, *args, **kwargs):
        """Set the tasks_number field as required"""
        super(TaskStartForm, self).__init__(*args, **kwargs)
        self.fields['tasks_number'].required = True


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'duration', 'registrations', 'registrations_details',
                  'feedback', 'feedback_details', 'stressful']
        widgets = {
            'procedure': forms.RadioSelect(choices=yes_no_doubt),
            'registrations': forms.CheckboxSelectMultiple(),
            'feedback': forms.RadioSelect(choices=yes_no),
            'stressful': forms.RadioSelect(choices=yes_no_doubt),
        }


class TaskEndForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['tasks_duration', 'tasks_stressful', 'tasks_stressful_details']
        widgets = {
            'tasks_stressful': forms.RadioSelect(choices=yes_no_doubt),
        }

    def __init__(self, *args, **kwargs):
        """Set the tasks_duration and tasks_stressful fields as required"""
        super(TaskEndForm, self).__init__(*args, **kwargs)

        tasks_duration = self.fields['tasks_duration']
        tasks_duration.required = True
        label = tasks_duration.label % self.instance.net_duration()
        tasks_duration.label = mark_safe(label)

        self.fields['tasks_stressful'].required = True

    def clean(self):
        """
        Check that the net duration is at least equal to the gross duration
        """
        cleaned_data = super(TaskEndForm, self).clean()

        tasks_duration = cleaned_data.get('tasks_duration')
        net_duration = self.instance.net_duration()
        if tasks_duration < net_duration:
            error = forms.ValidationError(_('Totale sessieduur moet minstens gelijk zijn aan netto sessieduur.'), code='comparison')
            self.add_error('tasks_duration', error)


class SessionEndForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = ['sessions_duration', 'sessions_stressful', 'sessions_stressful_details']
        widgets = {
            'sessions_stressful': forms.RadioSelect(choices=yes_no_doubt),
        }

    def __init__(self, *args, **kwargs):
        """Set the sessions_duration and sessions_stressful fields as required"""
        super(SessionEndForm, self).__init__(*args, **kwargs)

        sessions_duration = self.fields['sessions_duration']
        sessions_duration.required = True
        label = sessions_duration.label % self.instance.net_duration()
        sessions_duration.label = mark_safe(label)

        self.fields['sessions_stressful'].required = True

    def clean(self):
        """
        Check that the net duration is at least equal to the gross duration
        """
        cleaned_data = super(SessionEndForm, self).clean()

        sessions_duration = cleaned_data.get('sessions_duration')
        net_duration = self.instance.net_duration()
        if sessions_duration < net_duration:
            error = forms.ValidationError(_('Totale studieduur moet minstens gelijk zijn aan netto studieduur.'), code='comparison')
            self.add_error('sessions_duration', error)


class UploadConsentForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = ['informed_consent_pdf']

    def __init__(self, *args, **kwargs):
        super(UploadConsentForm, self).__init__(*args, **kwargs)
        self.fields['informed_consent_pdf'].required = True


class ProposalSubmitForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = ['date_submitted']

    approved = forms.BooleanField()
