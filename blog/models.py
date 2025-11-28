"""
Blog domain models.

Design:
- Posts go through different states (Draft/Published); ‘published’ manager encapsulates filter logic.
- Slugs: must be unique per publication date (SEO-friendly URLs).
- Favorites (user <-> post) are 1:n via join table with UniqueConstraint (no real composite PK in Django core).
"""

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


# Only delivers published posts (hard link to Post.Status.PUBLISHED).
# Attention: Status codes change => Adjust tests + manager.
class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)


# Post Model, define the fields of the model.That shows a Line in the Database.
class Post(models.Model):
    """
    A blog post.

    invariants:
    - ‘status’ is one of Status (2-digit code for slim index).
    - Default sorting by ‘-publish’ (newest first).
    - Slug uniqueness: per day via ‘unique_for_date’ (see field definition).
    """

    class Status(models.TextChoices):
        DRAFT = "DF", "Draft"
        PUBLISHED = "PB", "Published"

    # Fields
    # Title is a Char-field with a max length of 250 characters.
    title = models.CharField(max_length=250)
    # Unique slug per ‘publish’ date -> stable, date-based permalinks.
    # (show unique_for_date / Constraint below)
    slug = models.SlugField(max_length=250, unique_for_date="publish")
    # No default user: Author must be set explicitly (transparency in Admin/API).
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="blog_posts",
        default=1,
    )
    # Body is a TextField.
    body = models.TextField()
    # Publish and created_at and updated is a DateTimeField.
    publish = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    # Status is a CharField with a max length of 2 characters. It can be only the Decelerated ones from the Status class.
    status = models.CharField(
        max_length=2, choices=Status.choices, default=Status.DRAFT
    )

    # Managers
    objects = models.Manager()  # The default manager.
    published = PublishedManager()  # Our customer manager

    # Meta class
    class Meta:
        ordering = ["-publish"]
        indexes = [
            models.Index(fields=["-publish"]),
        ]

    # Methods
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
            "blog:post_detail",
            args=[self.publish.year, self.publish.month, self.publish.day, self.slug],
        )


# No composite PKs in Django core. Uniqueness (user, post) via UniqueConstraint.
# Advantage: simple foreign keys, compatible with Admin and migrations.
class FavoritePost(models.Model):
    # Composite Primary Key.
    pk = models.CompositePrimaryKey("user", "post")
    # Foreign Keys.
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey("blog.Post", on_delete=models.CASCADE)
    # Date and Time.
    created_at = models.DateTimeField(auto_now_add=True)


# Comment Model for user comments on posts.
# Comments are linked to Posts via ForeignKey.
# @ post: The Post to which the comment belongs.
class Comment(models.Model):
    # Foreign Key. The Post to which the comment belongs.
    # if we don't use related_name, Django will use comment_set as default.
    # Related Name can be used in views.py for the object name.
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    # Fields
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    # Meta class
    # Default ordering by ‘created’ (oldest first).
    class Meta:
        ordering = ["created"]
        indexes = [
            models.Index(fields=["created"]),
        ]

    # Methods
    # String representation of the Comment model.
    def __str__(self):
        return f"Comment by {self.name} on {self.post}"
