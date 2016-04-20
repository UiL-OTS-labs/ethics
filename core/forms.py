from django import forms
from django.utils.translation import ugettext as _


class ConditionalModelForm(forms.ModelForm):
    def check_dependency(self, cleaned_data, f1, f2, error_message=''):
        is_required = False
        if not error_message:
            error_message = _('Dit veld is verplicht.')
        if cleaned_data.get(f1) and not cleaned_data.get(f2):
            is_required = True
            self.add_error(f2, forms.ValidationError(error_message, code='required'))
        return is_required

    def check_dependency_singular(self, cleaned_data, f1, f1_field, f2, error_message=''):
        is_required = False
        if not error_message:
            error_message = _('Dit veld is verplicht.')
        if cleaned_data.get(f1):
            if getattr(cleaned_data.get(f1), f1_field) and not cleaned_data.get(f2):
                is_required = True
                self.add_error(f2, forms.ValidationError(error_message, code='required'))
        return is_required

    def check_dependency_multiple(self, cleaned_data, f1, f1_field, f2, error_message=''):
        is_required = False
        if not error_message:
            error_message = _('Dit veld is verplicht.')
        if cleaned_data.get(f1):
            for item in cleaned_data.get(f1):
                if getattr(item, f1_field) and not cleaned_data.get(f2):
                    is_required = True
                    self.add_error(f2, forms.ValidationError(error_message, code='required'))
                    break
        return is_required