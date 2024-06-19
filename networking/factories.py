# factories.py

"""
This file defines factory classes for creating test instances of UserData and 
FriendRequest models using factory_boy.
"""

import factory
from django.contrib.auth.hashers import make_password

from .models import FriendRequest, UserData


class UserDataFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating UserData instances with unique emails and hashed passwords.
    """

    class Meta:
        model = UserData

    email = factory.Sequence(lambda n: f"test{n}@example.com")
    name = factory.Faker("name")
    password = make_password("admin12345")


class FriendRequestFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating FriendRequest instances with default 'pending' status.
    """

    class Meta:
        model = FriendRequest

    sender = factory.SubFactory(UserDataFactory)
    receiver = factory.SubFactory(UserDataFactory)
    status = "pending"
    timestamp = factory.Faker("date_time")
