from django.db import models
from django.core.validators import MaxValueValidator
from django.utils.translation import ugettext_lazy as _

from core.models import Setting
from core.validators import validate_pdf_or_doc
from studies.models import Study


class Observation(models.Model):
    setting = models.ManyToManyField(
        Setting,
        verbose_name=_('Geef aan waar de dataverzameling plaatsvindt'))
    setting_details = models.CharField(
        _('Namelijk'),
        max_length=200,
        blank=True)
    supervision = models.NullBooleanField(
        _('Vindt het afnemen van de taak plaats onder het toeziend oog \
van de leraar of een ander persoon die bevoegd is?')
    )
    days = models.PositiveIntegerField(
        _('Op hoeveel dagen wordt er geobserveerd?'))
    mean_hours = models.DecimalField(
        _('Hoeveel uur wordt er gemiddeld per dag geobserveerd?'),
        max_digits=4,
        decimal_places=2,
        validators=[MaxValueValidator(24)])
    is_anonymous = models.BooleanField(
        _('Wordt er anoniem geobserveerd?'),
        help_text=_('Zoals zou kunnen voorkomen op fora en de onderzoeker ook een account heeft.'),
        default=False)
    is_in_target_group = models.BooleanField(
        _('Doet de onderzoeker zich voor als behorende tot de doelgroep?'),
        default=False)
    is_nonpublic_space = models.BooleanField(
        _('Wordt er geobserveerd in een niet-openbare ruimte?'),
        help_text=_('Bijvoorbeeld er wordt geobserveerd bij iemand thuis, \
tijdens een hypotheekgesprek of tijdens politieverhoren.'),
        default=False)
    has_advanced_consent = models.BooleanField(
        _('Vindt de informed consent van tevoren plaats?'),
        default=True)
    needs_approval = models.BooleanField(
        _('Heeft u toestemming nodig van een (samenwerkende) instantie \
om deze observatie te mogen uitvoeren?'),
        default=False)
    approval_institution = models.CharField(
        _('Welke instantie?'),
        max_length=200,
        blank=True)
    approval_document = models.FileField(
        _('Upload hiet het toestemmingsdocument (in .pdf of .doc(x)-formaat)'),
        blank=True,
        validators=[validate_pdf_or_doc])

    # References
    study = models.OneToOneField(Study)


class Registration(models.Model):
    order = models.PositiveIntegerField(unique=True)
    description = models.CharField(max_length=200)
    needs_details = models.BooleanField(default=False)

    class Meta:
        ordering = ['order']

    def __unicode__(self):
        return self.description


class Location(models.Model):
    name = models.CharField(_('Locatie'), max_length=200)
    registrations = models.ManyToManyField(
        Registration,
        verbose_name=_('Hoe wordt het gedrag geregistreerd?'))
    registrations_details = models.CharField(
        _('Namelijk'),
        max_length=200,
        blank=True)
    observation = models.ForeignKey(Observation)

    def __unicode__(self):
        return self.name