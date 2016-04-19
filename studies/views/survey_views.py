from django.core.urlresolvers import reverse

from braces.views import LoginRequiredMixin
from extra_views import UpdateWithInlinesView

from core.views import UserAllowedMixin, success_url

from ..forms import SurveyForm, SurveysInline
from ..models import Study, Survey


# NOTE: below view is non-standard, as it include inlines
# NOTE: no success message will be generated: https://github.com/AndrewIngram/django-extra-views/issues/59
class StudySurvey(LoginRequiredMixin, UserAllowedMixin, UpdateWithInlinesView):
    model = Study
    form_class = SurveyForm
    inlines = [SurveysInline]
    template_name = 'studies/survey_form.html'

    def forms_valid(self, form, inlines):
        """Removes existing Surveys if has_surveys is set to False."""
        if not form.instance.has_surveys:
            Survey.objects.filter(study=form.instance).delete()
            inlines = []
        return super(StudySurvey, self).forms_valid(form, inlines)

    def get_success_url(self):
        return success_url(self)

    def get_next_url(self):
        return reverse('proposals:submit', args=(self.object.pk,))

    def get_back_url(self):
        return reverse('studies:consent', args=(self.object.last_study().pk,))
