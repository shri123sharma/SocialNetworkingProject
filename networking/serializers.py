from rest_framework import serializers

from .models import FriendRequest, UserData


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for UserData model.
    """

    class Meta:
        model = UserData
        fields = ["id", "email", "name", "password"]

    def create(self, validated_data):
        """
        Create and return a new UserData instance, given the validated data.
        """
        user = UserData.objects.create(
            email=validated_data["email"], name=validated_data.get("name", "")
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class FriendRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for FriendRequest model.
    """

    class Meta:
        model = FriendRequest
        fields = ["id", "sender", "receiver", "status", "timestamp"]
