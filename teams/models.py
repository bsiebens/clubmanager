#  Copyright (c) ClubManager - Bernard Siebens 2024.

from datetime import date

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields import AutoSlugField
from rules import is_superuser
from rules.contrib.models import RulesModel

from members.models import Member


class Season(RulesModel):
    """A season groups information together in time."""

    start_date = models.DateField(_("start date"))
    end_date = models.DateField(_("end date"))

    class Meta:
        verbose_name = _("season")
        verbose_name_plural = _("seasons")
        ordering = ["start_date"]
        rules_permissions = {"add": is_superuser, "view": is_superuser, "change": is_superuser, "delete": is_superuser}

    def __str__(self):
        return f"{self.start_date} - {self.end_date}"

    @classmethod
    def get_season(cls, current_date: date | None = None, values_only: bool = False) -> "tuple[date, date] | Season":
        """Returns the season object that contains the given date, by default will use the current date."""
        if current_date is None:
            current_date = timezone.now().date()

        season = cls.objects.get(start_date__lte=current_date, end_date__gte=current_date)

        if values_only:
            return season.start_date, season.end_date

        return season

    @property
    def current_season(self) -> bool:
        return self.start_date <= timezone.now().date() <= self.end_date

    @property
    def passed_start_date(self) -> bool:
        return self.start_date <= timezone.now().date()

class NumberPool(RulesModel):
    """A number pool consists of a pool of numbers (hence the name) that can be handed out to players. Depending on settings you can enforce unique numbers in a given pool (e.g., to avoid 2 players in a youth category to have the same number. The default number pool will allow duplicate numbers to be assigned."""
    name = models.CharField(_("name"), max_length=255, unique=True)
    enforce_unique_numbers = models.BooleanField(_("enforce unique numbers"), default=False, help_text=_("Does not allow duplicate numbers to be assigned when checked"))

    class Meta:
        verbose_name = _("number pool")
        verbose_name_plural = _("number pools")
        rules_permissions = {"add": is_superuser, "view": is_superuser, "change": is_superuser, "delete": is_superuser}

    def __str__(self):
        return self.name


class TeamRole(RulesModel):
    """A team role defines the position of a member in a given team and can grant additional rights."""

    name = models.CharField(_("name"), max_length=250, unique=True)
    abbreviation = models.CharField(_("abbreviation"), max_length=250, unique=True, help_text=_("An abbreviated version of the role name"))

    staff_role = models.BooleanField(_("staff role"), default=False, help_text=_("Staff roles are exported under the staff section for a given team"))
    admin_role = models.BooleanField(_("admin role"), default=False, help_text=_("An admin role will grant rights to the user to manage and maintain a given team"))
    sort_order = models.PositiveIntegerField(
        _("sort order"),
        default=10,
        help_text=_("By adjusting the sort order, you can control which roles are displayed first, roles are ordered first based on order (low to high) before sorted by alphabet"),
    )

    created = models.DateTimeField(_("created"), auto_now_add=True)
    modified = models.DateTimeField(_("modified"), auto_now=True)

    class Meta:
        verbose_name = _("team role")
        verbose_name_plural = _("team roles")
        ordering = ["sort_order", "name"]
        rules_permissions = {"add": is_superuser, "view": is_superuser, "change": is_superuser, "delete": is_superuser}

    def __str__(self):
        return self.name

class Team(RulesModel):
    """Stores information on a given team. A team can be an internal team (i.e., something composed for a given tournament) or an external one (e.g., a competition team)"""

    class TeamTypes(models.TextChoices):
        INTERNAL = "INT", _("Internal")
        EXTERNAL = "EXT", _("External")

    name = models.CharField(_("name"), max_length=250, unique=True)
    short_name = models.CharField(_("short name"), max_length=250, unique=True, help_text=_("An optional short name"), blank=True, null=True)
    slug = AutoSlugField(_("slug"), max_length=250, populate_from="name", unique=True, editable=True, overwrite_on_add=False)
    type = models.CharField(_("type"), max_length=3, choices=TeamTypes.choices, default=TeamTypes.EXTERNAL, help_text=_("Internal teams are not accessible through the API"))
    number_pool = models.ForeignKey(NumberPool, verbose_name=_("number pool"), on_delete=models.SET_DEFAULT, default="default", to_field="name")
    logo = models.ImageField(_("logo"), upload_to="teams/logo/", null=True, blank=True)

    members = models.ManyToManyField(Member, verbose_name=_("members"), through="TeamMembership")

    created = models.DateTimeField(_("created"), auto_now_add=True)
    modified = models.DateTimeField(_("modified"), auto_now=True)

    class Meta:
        verbose_name = _("team")
        verbose_name_plural = _("teams")
        ordering = ["name"]
        rules_permissions = {"add": is_superuser, "view": is_superuser, "change": is_superuser, "delete": is_superuser}

    def __str__(self):
        return self.name

    def get_short_name(self) -> str:
        """Returns the short name, or falls back to the full name if no short name is provided"""
        if self.short_name is not None and self.short_name != "":
            return self.short_name

        return self.name

class TeamMembership(RulesModel):
    team = models.ForeignKey(Team, verbose_name=_("team"), on_delete=models.CASCADE)
    member = models.ForeignKey(Member, verbose_name=_("member"), on_delete=models.CASCADE)