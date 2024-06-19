from django.urls import path
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from .views import (ListFriendsView, ListPendingRequestsView, RegisterView,
                    RespondFriendRequestView, SearchUserView,
                    SendFriendRequestView)

urlpatterns = [
    # Endpoint to obtain JWT token pair (access and refresh tokens)
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    # Endpoint to refresh JWT access token
    path("login/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Endpoint to register a new user
    path("register/", RegisterView.as_view(), name="sign_up"),
    # Endpoint to search users by keyword
    path("search/", SearchUserView.as_view(), name="search_users"),
    # Endpoint to send a friend request to a user identified by to_user_id
    path(
        "friend-request/send/<int:to_user_id>/",
        SendFriendRequestView.as_view(),
        name="send_friend_request",
    ),
    # Endpoint to respond to a friend request identified by request_id with action (accept/reject)
    path(
        "friend-request/respond/<int:request_id>/<str:action>/",
        RespondFriendRequestView.as_view(),
        name="respond_to_friend_request",
    ),
    # Endpoint to list friends of the authenticated user
    path("friends/", ListFriendsView.as_view(), name="list_friends"),
    # Endpoint to list pending friend requests for the authenticated user
    path(
        "friend-requests/pending/",
        ListPendingRequestsView.as_view(),
        name="list_pending_requests",
    ),
]
