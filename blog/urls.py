from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    # ^ Post views
    # List view
    path("", views.PostListView.as_view(), name="post_list"),
    # Detail view
    path(
        "<int:year>/<int:month>/<int:day>/<slug:post>/",
        views.post_detail,
        name="post_detail",
    ),
    # Share views
    path("<int:post_id>/share/", views.post_share, name="post_share"),
]
