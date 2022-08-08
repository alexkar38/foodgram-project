from django.urls import path

from .views import FollowListView, FollowView

urlpatterns = [
    path("users/<int:id>/subscribe/", FollowView.as_view(), name="subscribe"),
    path(
        "users/subscriptions/", FollowListView.as_view(), name="subscription"
    ),
]
