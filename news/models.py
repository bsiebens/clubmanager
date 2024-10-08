from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields import AutoSlugField
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
from rules.contrib.models import RulesModel

from teams.models import Team
from .rules import is_admin, is_author, is_released, is_editor


class NewsItem(RulesModel):
    """A news item. This can be both an internal as well as an external message."""

    class StatusChoices(models.IntegerChoices):
        DRAFT = 0, _("Draft")
        IN_REVIEW = 1, _("In Review")
        RELEASED = 2, _("Released")

    class NewsItemTypeChoices(models.IntegerChoices):
        INTERNAL = 0, _("Internal")
        EXTERNAL = 1, _("External")
        INTERNAL_EXTERNAL = 2, _("Internal & External")

    title = models.CharField(_("title"), max_length=250)
    text = MarkdownxField(_("text"))
    slug = AutoSlugField(populate_from=["title"], verbose_name=_("slug"))
    author = models.ForeignKey(get_user_model(), verbose_name=_("author"), on_delete=models.PROTECT)
    status = models.IntegerField(_("status"), choices=StatusChoices.choices, default=StatusChoices.DRAFT)
    type = models.IntegerField(
        _("type"),
        choices=NewsItemTypeChoices.choices,
        default=NewsItemTypeChoices.INTERNAL,
        help_text=_("Internal news is only visible to members after logging in. External news will be published on the website."),
    )
    publish_on = models.DateTimeField(
        _("Publish on"), default=timezone.now, help_text="Date and time on which this item should be published. Only released items will be posted."
    )

    teams = models.ManyToManyField(Team, related_name="news_items")

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("news item")
        verbose_name_plural = _("news items")
        ordering = ["-created"]
        rules_permissions = {"add": is_admin, "view": is_author | is_released, "change": is_author | is_editor, "delete": is_author | is_editor, "release": is_editor}

    def formatted(self) -> str:
        return markdownify(self.text)

    def main_picture(self) -> "Picture":
        try:
            return self.pictures.get(main_picture=True)
        except Picture.DoesNotExist:
            return None

    @property
    @admin.display(description=_("Author"))
    def author_name(self):
        return self.author.get_full_name()


class Picture(models.Model):
    """A picture linked to a news item."""

    news_item = models.ForeignKey(NewsItem, on_delete=models.CASCADE, related_name="pictures", verbose_name=_("news item"))
    picture = models.ImageField(_("picture"), upload_to="news/pictures/")
    main_picture = models.BooleanField(_("main picture"), default=False, help_text=_("The main picture is the picture shown on the cover of the news item."))

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.picture.name

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["news_item", "main_picture"],
                condition=models.Q(main_picture=True),
                name="news_item_main_picture_unique",
                violation_error_message=_("Only one picture can be the main picture for a news item"),
            )
        ]
