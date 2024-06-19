"""
Unit tests for API views using Django's APITestCase and factory_boy for data generation.

Covering registration, user search, friend requests (send, respond), and friend management (list friends, pending requests).

Tests include scenarios for successful operations, error handling, and authentication checks.
"""

from datetime import datetime, timedelta

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .factories import FriendRequestFactory, UserDataFactory
from .models import FriendRequest, UserData


class RegisterViewTestCase(APITestCase):
    def test_successful_registration(self):
        url = reverse("sign_up")
        data = {
            "username": "testuser",
            "password": "testpass",
            "email": "test@example.com",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_registration_with_invalid_data(self):
        url = reverse("sign_up")
        data = {"username": "", "password": "testpass", "email": "invalid-email"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class SearchUserViewTestCase(APITestCase):
    def setUp(self):
        self.user = UserDataFactory(email="test@gmail.com", name="test")
        self.client = APIClient()

        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

    def test_search_user_with_valid_keyword(self):
        UserDataFactory(email="root@gmail.com", name="root")
        UserDataFactory(email="test1@gmail.com", name="test1")

        url = reverse("search_users")
        response = self.client.get(url, {"keyword": "test1@gmail.com"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data["results"]), 0)

    def test_search_user_with_no_keyword(self):
        url = reverse("search_users")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_user_with_no_results(self):
        url = reverse("search_users")
        response = self.client.get(url, {"keyword": "nonexistent"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class SendFriendRequestViewTestCase(APITestCase):
    def setUp(self):
        self.user1 = UserDataFactory(email="test1@gmail.com", name="test1")
        self.user2 = UserDataFactory(email="test2@gmail.com", name="test2")
        self.user3 = UserDataFactory(email="test3@gmail.com", name="test3")

        self.client = APIClient()

        refresh = RefreshToken.for_user(self.user1)
        self.access_token = str(refresh.access_token)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

    def test_send_friend_request_to_self(self):
        url = reverse("send_friend_request", kwargs={"to_user_id": self.user1.id})
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["error"], "Cannot send friend request to yourself"
        )

    def test_send_duplicate_friend_request(self):
        FriendRequestFactory(sender=self.user1, receiver=self.user2, status="pending")

        url = reverse("send_friend_request", kwargs={"to_user_id": self.user2.id})
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Friend request already sent")

    def test_send_too_many_friend_requests(self):
        one_minute_ago = datetime.now() - timedelta(minutes=1)
        fr1 = FriendRequestFactory(
            sender=self.user1,
            receiver=self.user2,
            status="pending",
            timestamp=one_minute_ago + timedelta(seconds=10),
        )
        fr2 = FriendRequestFactory(
            sender=self.user1,
            receiver=self.user3,
            status="pending",
            timestamp=one_minute_ago + timedelta(seconds=20),
        )
        fr3 = FriendRequestFactory(
            sender=self.user1,
            receiver=self.user2,
            status="pending",
            timestamp=one_minute_ago + timedelta(seconds=30),
        )

        FriendRequest.objects.filter(id=fr1.id).update(
            timestamp=one_minute_ago + timedelta(seconds=10)
        )
        FriendRequest.objects.filter(id=fr2.id).update(
            timestamp=one_minute_ago + timedelta(seconds=20)
        )
        FriendRequest.objects.filter(id=fr3.id).update(
            timestamp=one_minute_ago + timedelta(seconds=30)
        )

        url = reverse("send_friend_request", kwargs={"to_user_id": self.user3.id})
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_send_friend_request_success(self):
        url = reverse("send_friend_request", kwargs={"to_user_id": self.user2.id})
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "Friend request sent")


class RespondFriendRequestViewTestCase(APITestCase):
    def setUp(self):
        self.user1 = UserDataFactory(email="test1@gmail.com", name="test1")
        self.user2 = UserDataFactory(email="user1@gmail.com", name="user1")

        self.friend_request = FriendRequestFactory(
            sender=self.user1, receiver=self.user2, status="pending"
        )

        refresh = RefreshToken.for_user(self.user1)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

    def test_accept_friend_request(self):
        url = reverse(
            "respond_to_friend_request",
            kwargs={"request_id": self.friend_request.id, "action": "accept"},
        )
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Friend request accepted")

    def test_reject_friend_request(self):
        url = reverse(
            "respond_to_friend_request",
            kwargs={"request_id": self.friend_request.id, "action": "reject"},
        )
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Friend request rejected")

    def test_invalid_action(self):
        url = reverse(
            "respond_to_friend_request",
            kwargs={"request_id": self.friend_request.id, "action": "invalid_action"},
        )
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Invalid response")


class ListFriendsViewTestCase(APITestCase):
    def setUp(self):
        self.user1 = UserDataFactory(email="test1@gmail.com", name="test1")
        self.user2 = UserDataFactory(email="root@gmail.com", name="root")
        self.user3 = UserDataFactory(email="index2@gmail.com", name="index2")
        self.user4 = UserDataFactory(email="nofriends@gmail.com", name="nofriends")

        # Create friend relationships
        FriendRequestFactory(sender=self.user1, receiver=self.user2, status="accepted")
        FriendRequestFactory(sender=self.user1, receiver=self.user3, status="accepted")
        FriendRequestFactory(sender=self.user3, receiver=self.user1, status="accepted")

        # Authenticate user1
        refresh = RefreshToken.for_user(self.user1)
        self.access_token = str(refresh.access_token)

        refresh_no_friend = RefreshToken.for_user(self.user4)
        self.access_token_no_friend = str(refresh_no_friend.access_token)

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

    def test_list_friends_success(self):
        url = reverse("list_friends")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_no_friends(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.access_token_no_friend}"
        )
        url = reverse("list_friends")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data.get("message", None), "You have no friends")

    def test_unauthenticated_access(self):
        self.client.credentials()
        url = reverse("list_friends")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ListPendingRequestsViewTestCase(APITestCase):
    def setUp(self):
        self.user1 = UserDataFactory(email="test1@gmail.com", name="Test1")
        self.user2 = UserDataFactory(email="test2@gmail.com", name="Test2")
        self.user3 = UserDataFactory(email="test3@gmail.com", name="Test3")

        FriendRequestFactory(sender=self.user2, receiver=self.user1, status="pending")
        FriendRequestFactory(sender=self.user3, receiver=self.user1, status="pending")

        refresh = RefreshToken.for_user(self.user1)
        self.access_token = str(refresh.access_token)

        refresh_user_no_pending = RefreshToken.for_user(self.user3)
        self.access_token_user_no_pending = str(refresh_user_no_pending.access_token)

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

    def test_list_pending_requests(self):
        url = reverse("list_pending_requests")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_no_pending_requests(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.access_token_user_no_pending}"
        )
        url = reverse("list_pending_requests")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(
            response.data.get("message", None), "You have no pending friend requests"
        )

    def test_unauthenticated_access(self):
        self.client.credentials()
        url = reverse("list_pending_requests")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
