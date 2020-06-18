from django.conf import settings
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.utils.functional import cached_property
from django.utils.translation import ugettext as _
from django.views.generic.base import ContextMixin
from django.views.generic.detail import SingleObjectMixin

from core.utils import get_all_secretaries, is_secretary

from .models import Decision, Review
from .utils import auto_review


class UserAllowedMixin(SingleObjectMixin):
    def get_object(self, queryset=None):
        """
        Checks whether the current User is a reviewer in this Review,
        as well as whether the Review is still open.
        """
        obj = super(UserAllowedMixin, self).get_object(queryset)
        current_user = self.request.user

        if isinstance(obj, Review):
            secretary_reviewers = obj.decision_set.filter(reviewer__groups__name=settings.GROUP_SECRETARY)
            if secretary_reviewers and is_secretary(current_user):
                return obj
            if not obj.decision_set.filter(reviewer=current_user):
                raise PermissionDenied

        if isinstance(obj, Decision):
            reviewer = obj.reviewer
            date_end = obj.review.date_end

            if date_end:
                raise PermissionDenied
            if ( self.request.user != reviewer ) and \
                not ( is_secretary(reviewer) and is_secretary(current_user) ):
                    raise PermissionDenied
                
        return obj


class CommitteeMixin(ContextMixin):

    @cached_property
    def committee(self):
        group = self.kwargs.get('committee')

        return Group.objects.get(name=group)

    @cached_property
    def committee_display_name(self):
        committee = _('Algemene Kamer')

        if self.committee.name == 'LK':
            committee = _('Linguïstiek Kamer')

        return committee

    def get_context_data(self, **kwargs):
        context = super(CommitteeMixin, self).get_context_data(**kwargs)

        context['committee'] = self.committee
        context['committee_name'] = self.committee_display_name

        return context


class AutoReviewMixin(object):
    def get_context_data(self, **kwargs):
        """Adds the results of the machine-wise review to the context."""
        context = super(AutoReviewMixin, self).get_context_data(**kwargs)
        reasons = auto_review(self.get_object().proposal)
        context['auto_review_go'] = len(reasons) == 0
        context['auto_review_reasons'] = reasons
        return context
