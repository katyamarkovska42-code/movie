from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        max_length=128
    )

    password_confirm = serializers.CharField(
        write_only=True,
        max_length=128
    )

    email = serializers.EmailField(
        required=True,
        max_length=254
    )

    username = serializers.CharField(
        required=True,
        max_length=150
    )

    first_name = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=150
    )

    last_name = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=150
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
            "password_confirm",
        ]
        read_only_fields = ["id"]

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({
                "password_confirm": "Паролі не збігаються."
            })

        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")

        return User.objects.create_user(
            password=password,
            **validated_data
        )
