from datetime import datetime, timedelta

from django.db.models import Q
from django.shortcuts import render
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import FriendRequest, UserData
from .serializers import FriendRequestSerializer, UserSerializer


class RegisterView(APIView):
    """
    View to handle user registration.

    POST request with user data to create a new user.
    """

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomPagination(PageNumberPagination):
    """
    Custom pagination class for paginated responses.

    Implements pagination with default page size of 10,
    max page size of 100, and includes links to next and
    previous pages in response.
    """

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data, status_code):
        return Response(
            {
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            },
            status=status_code,
        )


class SearchUserView(APIView):
    """
    View to search for users based on a keyword.

    GET request with 'keyword' query parameter to search for users
    by email, first name, or last name. Paginates the results.
    """

    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get(self, request):
        keyword = request.query_params.get("keyword", "")
        users = UserData.objects.filter(
            Q(email__iexact=keyword)
            | Q(email__icontains=keyword)
            | Q(first_name__icontains=keyword)
            | Q(last_name__icontains=keyword)
        ).order_by("email")
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(users, request)
        serializer = UserSerializer(result_page, many=True)
        if result_page:
            return paginator.get_paginated_response(serializer.data, status.HTTP_200_OK)
        else:
            return Response(
                {"message": "No results found."}, status=status.HTTP_404_NOT_FOUND
            )


class SendFriendRequestView(APIView):
    """
    View to send a friend request to another user.

    POST request with 'to_user_id' to send a friend request to
    the user identified by the given ID. Handles validation and
    rate limiting of friend requests.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, to_user_id):
        from_user = request.user
        to_user = UserData.objects.get(id=to_user_id)

        if from_user == to_user:
            return Response(
                {"error": "Cannot send friend request to yourself"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if FriendRequest.objects.filter(sender=from_user, receiver=to_user).exists():
            return Response(
                {"error": "Friend request already sent"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        one_minute_ago = datetime.now() - timedelta(minutes=1)
        recent_requests = FriendRequest.objects.filter(
            sender=from_user, timestamp__gte=one_minute_ago
        ).count()
        if recent_requests >= 3:
            return Response(
                {"error": "Too many friend requests. Try again later."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        FriendRequest.objects.create(
            sender=from_user, receiver=to_user, status="pending"
        )
        return Response(
            {"message": "Friend request sent"}, status=status.HTTP_201_CREATED
        )


class RespondFriendRequestView(APIView):
    """
    View to respond to a friend request.

    POST request with 'request_id' and 'action' (accept/reject) to
    accept or reject a friend request. Handles authorization, request
    validation, and updates the status of the friend request.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, request_id, action):
        try:
            friend_request = FriendRequest.objects.get(id=request_id)
        except FriendRequest.DoesNotExist:
            return Response(
                {"error": "Friend request not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if action not in ["accept", "reject"]:
            return Response(
                {"error": "Invalid response"}, status=status.HTTP_400_BAD_REQUEST
            )

        if action == "accept":
            friend_request.status = "accepted"
        elif action == "reject":
            friend_request.status = "rejected"
        friend_request.save()
        return Response(
            {"message": f"Friend request {action}ed"}, status=status.HTTP_200_OK
        )


class ListFriendsView(APIView):
    """
    View to list friends of the authenticated user.

    GET request to fetch a list of friends (users who have accepted
    friend requests) for the authenticated user.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        friends_ids = FriendRequest.objects.filter(
            (Q(sender=user) | Q(receiver=user)) & Q(status="accepted")
        ).values_list("sender_id", "receiver_id")
        friends_ids = [id for pair in friends_ids for id in pair if id != user.id]
        friends = UserData.objects.filter(id__in=friends_ids)
        if not friends.exists():
            return Response(
                {"message": "You have no friends"}, status=status.HTTP_204_NO_CONTENT
            )

        serializer = UserSerializer(friends, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ListPendingRequestsView(APIView):
    """
    View to list pending friend requests for the authenticated user.

    GET request to fetch a list of pending friend requests that the
    authenticated user has received and not yet responded to.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        pending_requests = FriendRequest.objects.filter(receiver=user, status="pending")
        serializer = FriendRequestSerializer(pending_requests, many=True)
        if not serializer.data:
            return Response(
                {"message": "You have no pending friend requests"},
                status=status.HTTP_204_NO_CONTENT,
            )
        return Response(serializer.data, status=status.HTTP_200_OK)
