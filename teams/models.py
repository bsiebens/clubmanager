import datetime

from django.contrib import admin
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields import AutoSlugField
from model_utils import FieldTracker
from rules.contrib.models import RulesModel

from members.models import Member
from members.rules import is_organization_admin
from .rules import is_team_admin
from news.rules import is_admin


def team_season_path(instance: "TeamPicture", filename: str) -> str:
    return "groups/picture/{instance.team.slug}/{instance.season.start_year}/{filename}".format(instance=instance, filename=filename)


class TeamManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return super(TeamManager, self).get_queryset().select_related("number_pool").prefetch_related("members")


class TeamMembershipManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return super(TeamMembershipManager, self).get_queryset().select_related("team", "member__user", "role", "season")


class Season(RulesModel):
    """A season of play"""

    start_date = models.DateField(_("start date"))
    end_date = models.DateField(_("end date"))

    def __str__(self):
        return _("Season '{start} - '{end}").format(start=self.start_date.strftime("%y"), end=self.end_date.strftime("%y"))

    class Meta:
        verbose_name = _("season")
        verbose_name_plural = _("seasons")
        ordering = ["start_date"]
        rules_permissions = {"add": is_organization_admin, "view": is_organization_admin, "change": is_organization_admin, "delete": is_organization_admin}

    @classmethod
    def get_season(cls, date: datetime.date = timezone.now(), return_values_only: bool = False) -> "list | Season":
        """
        Returns the season for the given date.

        * `date` date to check, default = `timezone.now()`
        * `return_values_only` if true, will only return start and end date, no object, default = `False`

        Raises `DoesNotExist` if no Season exists.
        """
        season = cls.objects.get(start_date__lte=date, end_date__gte=date)

        if return_values_only:
            return [season.start_date, season.end_date]
        return season

    @classmethod
    def get_season_id(cls, date: datetime.date = timezone.now()) -> int:
        season = Season.get_season(date=date, return_values_only=False)
        return season.id

    @property
    @admin.display(description=_("Current Season"), boolean=True)
    def current_season(self):
        today = timezone.now().date()

        return self.start_date <= today and self.end_date >= today

    @property
    def start_year(self) -> int:
        return self.start_date.strftime("%Y")

    def has_started(self) -> bool:
        return self.start_date < timezone.now().date()


class NumberPool(RulesModel):
    """A number pool holds all numbers that can be assigned, within a pool you can enforce unique numbers."""

    name = models.CharField(_("name"), max_length=250, unique=True)
    enforce_unique = models.BooleanField(_("enforce unique"), default=True, help_text=_("If selected will enforce unique numbers on all players"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("number pool")
        verbose_name_plural = _("number pools")
        rules_permissions = {"add": is_organization_admin, "view": is_organization_admin, "change": is_organization_admin, "delete": is_organization_admin}


class TeamRole(RulesModel):
    """Roles that can be assigned to team members"""

    name = models.CharField(_("name"), max_length=250, unique=True)
    abbreviation = models.CharField(_("abbreviation"), max_length=10, help_text=_("Abbreviated version of the name"), unique=True)
    staff_role = models.BooleanField(_("staff"), default=False, help_text=_("Staff roles are displayed on the team page under the staff section"))
    admin_role = models.BooleanField(_("admin"), default=False, help_text=_("Admin roles can manage the team (add/remove members, post messages, create events)"))
    sort_order = models.IntegerField(
        _("sort order"),
        default=100,
        help_text=_(
            "By adjusting the sort order this role will displayed higher on the team page, by default roles are sorted by order (low to high) and then alphabetically"
        ),
    )

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("team role")
        verbose_name_plural = _("team roles")
        ordering = ["sort_order", "name"]
        rules_permissions = {"add": is_organization_admin, "view": is_organization_admin, "change": is_organization_admin, "delete": is_organization_admin}


class Team(RulesModel):
    """A team"""

    class TeamTypes(models.TextChoices):
        INTERNAL = "INT", _("Internal")
        EXTERNAL = "EXT", _("External")

    name = models.CharField(_("name"), max_length=250)
    short_name = models.CharField(_("short name"), max_length=250, help_text=_("An optional short name"), blank=True, null=True)
    slug = AutoSlugField(populate_from=["name"], verbose_name=_("slug"), editable=True, overwrite_on_add=False)
    type = models.CharField(
        _("type"),
        max_length=3,
        choices=TeamTypes.choices,
        default=TeamTypes.INTERNAL,
        help_text=_("Internal groups are only visible to members, external groups are available via the API"),
    )
    number_pool = models.ForeignKey(NumberPool, on_delete=models.SET_DEFAULT, verbose_name=_("number pool"), to_field="name", default="default")
    logo = models.ImageField(_("logo"), upload_to="team/logo/")

    members = models.ManyToManyField(Member, verbose_name=_("members"), through="TeamMembership")

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    tracker = FieldTracker(fields=["slug"])

    objects = TeamManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("team")
        verbose_name_plural = _("teams")
        rules_permissions = {"add": is_organization_admin, "view": is_organization_admin, "change": is_organization_admin, "delete": is_organization_admin}
        ordering = ["name"]

    @property
    def get_short_name(self) -> str:
        """Returns short_name if exists, otherwise falls back to name"""
        if self.short_name is not None and self.short_name != "":
            return self.short_name

        return self.name


class TeamMembership(RulesModel):
    """Linking members to teams"""

    team = models.ForeignKey(Team, on_delete=models.CASCADE, verbose_name=_("team"))
    member = models.ForeignKey(Member, on_delete=models.CASCADE, verbose_name=_("member"))
    season = models.ForeignKey(Season, on_delete=models.PROTECT, verbose_name=_("season"))
    role = models.ForeignKey(TeamRole, on_delete=models.PROTECT, verbose_name=_("role"))

    number = models.IntegerField(_("number"), blank=True, null=True)
    captain = models.BooleanField(_("captain"), default=False, help_text=_("Mark as team captain"))
    assistant_captain = models.BooleanField(_("assistant captain"), default=False, help_text=_("Mark as assistant team captain"))

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    objects = TeamMembershipManager()

    def __str__(self):
        return _("{team} - {member}").format(team=self.team, member=self.member)

    class Meta:
        verbose_name = _("team membership")
        verbose_name_plural = _("team memberships")
        ordering = ["team__name", "role__sort_order", "number", "member__user__last_name", "member__user__first_name"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(number__gte=0) | models.Q(number__lte=99),
                name="number_0-99",
                violation_error_message=_("Number must be between 0 and 99"),
            ),
            models.UniqueConstraint(
                fields=["team", "season", "number"],
                name="team_season_number_unique",
                violation_error_message=_("Number already in use for this team in the current season"),
            ),
        ]
        rules_permissions = {
            "add": is_team_admin | is_organization_admin,
            "view": is_admin,
            "change": is_team_admin | is_organization_admin,
            "delete": is_team_admin | is_organization_admin,
        }

    """ def save(self, *args, **kwargs) -> None:
        update_group_membership(self.member.user.id)

        if self.tracker.has_changed("team"):
            if self.tracker.previous("team") is None:
                group = Group.objects.get(name=self.team.slug)

                self.member.user.groups.add(group)

            else:
                # Find all groups a member belongs to
                memberships = TeamMembership.objects.filter(season=Season.get_season(), member=self.member).exclude(id=self.id)
                teams = [membership.team.slug for membership in memberships]
                teams.append(self.team.slug)

                self.member.user.groups.set(Group.objects.filter(name__in=teams))

        super(TeamMembership, self).save(*args, **kwargs) """

    def clean(self) -> None:
        if self.number is not None and self.team.number_pool.enforce_unique:
            base_query = TeamMembership.objects.filter(number=self.number, team__number_pool=self.team.number_pool)

            if self.id is not None:
                base_query = base_query.exclude(pk=self.id)

            if base_query.count() > 0:
                raise ValidationError(_("Number already in use, please update to a unique number."))

        return super(TeamMembership, self).clean()


class TeamPicture(RulesModel):
    """A picture for a given team in a given season"""

    team = models.ForeignKey(Team, on_delete=models.CASCADE, verbose_name=_("team"))
    season = models.ForeignKey(Season, on_delete=models.PROTECT, verbose_name=_("season"))
    picture = models.ImageField(_("picture"), upload_to=team_season_path)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.picture.name

    class Meta:
        verbose_name = _("team picture")
        verbose_name_plural = _("team pictures")
        rules_permissions = {"add": is_organization_admin, "view": is_organization_admin, "change": is_organization_admin, "delete": is_organization_admin}
