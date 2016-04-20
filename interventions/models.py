from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.models import Setting
from studies.models import Study


class Intervention(models.Model):
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
    description = models.TextField(
        _('Beschrijf de interventie(s). Geef aan waar de interventie plaatsvindt en \
binnen hoeveel sessies. Geef een duidelijke beschrijving van wat de interventie inhoud en \
welke partijen er bij betrokken zijn.'))
    has_drawbacks = models.BooleanField(
        _('Is de interventie zodanig dat er voor de deelnemers ook nadelen aan verbonden kunnen zijn?'),
        help_text=_('Denk aan een verminderde leeropbrengst, een minder effectief 112-gesprek, \
een slechter adviesgesprek, een ongunstiger beoordeling, etc'),
        default=False)
    has_drawbacks_details = models.TextField(
        _('Licht toe'),
        blank=True)
    is_supervised = models.BooleanField(
        _('Vindt de interventie plaats onder het toezicht \
van een een bevoegd persoon die, wanneer de interventie niet zou plaatsvinden, er ook zou zijn. \
Zoals een leraar of logopedist.'),
        default=True)

    # References
    study = models.OneToOneField(Study)