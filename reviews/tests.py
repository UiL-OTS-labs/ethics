from datetime import datetime

from django.test import TestCase
from django.contrib.auth.models import User, Group

from .models import Review, Decision
from .utils import start_review, auto_review
from proposals.models import Proposal, Study, Session, Task, Relation, Compensation, Registration, AgeGroup
from proposals.utils import generate_ref_number


class BaseReviewTestCase(TestCase):
    fixtures = ['relations', 'compensations', 'registrations', 'agegroups', 'groups']

    def setUp(self):
        """
        Sets up the Users and a default Proposal to use in the tests below.
        """
        self.secretary = User.objects.create_user('secretary', 'test@test.com', 'secret')
        self.c1 = User.objects.create_user('c1', 'test@test.com', 'secret')
        self.c2 = User.objects.create_user('c2', 'test@test.com', 'secret')
        self.user = User.objects.create_user('user', 'test@test.com', 'secret')
        self.supervisor = User.objects.create_user('supervisor', 'test@test.com', 'secret')

        self.secretary.groups.add(Group.objects.get(name='Secretaris'))
        self.c1.groups.add(Group.objects.get(name='Commissie'))
        self.c2.groups.add(Group.objects.get(name='Commissie'))

        self.proposal = Proposal.objects.create(title='p1', reference_number=generate_ref_number(self.user),
                                                date_start=datetime.now(), date_end=datetime.now(),
                                                created_by=self.user, supervisor=self.supervisor,
                                                relation=Relation.objects.get(pk=4))
        self.study = Study.objects.create(proposal=self.proposal, compensation=Compensation.objects.get(pk=1))


class ReviewTestCase(BaseReviewTestCase):
    def test_start_review(self):
        """
        Tests starting of a Review from a submitted Proposal.
        """
        # If the Relation on a Proposal requires a supervisor, a Review for the supervisor should be started.
        review = start_review(self.proposal)
        self.assertEqual(review.stage, Review.SUPERVISOR)
        self.assertEqual(Decision.objects.filter(reviewer=self.supervisor).count(), 1)
        self.assertEqual(Decision.objects.filter(review=review).count(), 1)
        self.assertEqual(review.decision_set.count(), 1)

        # If the Relation on a Proposal does not require a supervisor, a assignment review should be started.
        self.proposal.relation = Relation.objects.get(pk=5)
        self.proposal.save()
        review = start_review(self.proposal)
        self.assertEqual(review.stage, Review.ASSIGNMENT)
        self.assertEqual(Decision.objects.filter(reviewer=self.secretary).count(), 1)
        self.assertEqual(Decision.objects.filter(review=review).count(), 1)
        self.assertEqual(review.decision_set.count(), 1)


class SupervisorTestCase(BaseReviewTestCase):
    def test_decision_supervisor(self):
        """
        Tests whether a Decision from the supervisor leads to a change in the Review.
        """
        review = start_review(self.proposal)
        self.assertEqual(review.go, None)

        decision = Decision.objects.filter(review=review)[0]
        decision.go = True
        decision.save()
        review.refresh_from_db()
        self.assertEqual(review.go, True)


class AssignmentTestCase(BaseReviewTestCase):
    def test_assignment(self):
        """
        Tests whether the assignment works correctly.
        """
        pass


class CommissionTestCase(BaseReviewTestCase):
    def test_decision_commission(self):
        """
        Tests whether the commission phase in a Review works correctly.
        """
        # Set the relation to a supervisor so we can skip the first phase
        self.proposal.relation = Relation.objects.get(pk=5)
        self.proposal.save()
        review = start_review(self.proposal)
        self.assertEqual(review.stage, Review.ASSIGNMENT)
        self.assertEqual(review.go, None)

        # Create a Decision for a member of the commission group
        Decision.objects.create(review=review, reviewer=self.c1)
        review.stage = Review.COMMISSION
        review.refresh_from_db()

        decisions = Decision.objects.filter(review=review)
        self.assertEqual(len(decisions), 2)

        decisions[0].go = True
        decisions[0].save()
        review.refresh_from_db()
        self.assertEqual(review.go, None)  # undecided

        decisions[1].go = False
        decisions[1].save()
        review.refresh_from_db()
        self.assertEqual(review.go, False)  # no go

        decisions[1].go = True
        decisions[1].save()
        review.refresh_from_db()
        self.assertEqual(review.go, True)  # go


class AutoReviewTests(BaseReviewTestCase):
    def test_auto_review(self):
        self.study.age_groups = AgeGroup.objects.filter(pk=4)  # adolescents
        self.study.save()

        go, reasons = auto_review(self.proposal)
        self.assertTrue(go)

        s1 = Session.objects.create(study=self.study, order=1, tasks_number=1)

        s1_t1 = Task.objects.create(session=s1, order=1)
        s1_t1.registrations = Registration.objects.filter(pk=6)  # psychofysiological measurements
        s1_t1.save()

        go, reasons = auto_review(self.proposal)
        self.assertFalse(go)
        self.assertEqual(len(reasons), 1)

        s1_t1.registrations = Registration.objects.filter(requires_review=True)  # psychofysiological measurements / other
        s1_t1.save()

        go, reasons = auto_review(self.proposal)
        self.assertFalse(go)
        self.assertEqual(len(reasons), 2)

        self.study.risk = True
        self.study.save()

        go, reasons = auto_review(self.proposal)
        self.assertFalse(go)
        self.assertEqual(len(reasons), 3)
