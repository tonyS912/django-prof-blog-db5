from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    # ^ Post views
    # List view
    path("", views.post_list, name="post_list"),
    # Chapter 01 = path("", views.PostListView.as_view(), name="post_list"),
    # Detail view
    path(
        "<int:year>/<int:month>/<int:day>/<slug:post>/",
        views.post_detail,
        name="post_detail",
    ),
    # Share views
    path("<int:post_id>/share/", views.post_share, name="post_share"),
    # Comment Views
    path("<int:post_id>/comment/", views.post_comment, name="post_comment"),
    # Tag views
    path("tag/<slug:tag_slug>/", views.post_list, name="post_list_by_tag"),
]
