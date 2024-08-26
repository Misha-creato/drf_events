from rest_framework import serializers

from users.models import CustomUser


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    confirm_password = serializers.CharField(
        max_length=128,
    )

    class Meta:
        model = CustomUser
        fields = [
            'email',
            'password',
            'confirm_password',
        ]

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError(
                'Пароли не совпадают'
            )
        return attrs


class AuthSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        max_length=128,
    )


class RefreshAndLogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class PasswordRestoreRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordRestoreSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        max_length=128,
    )
    confirm_password = serializers.CharField(
        max_length=128,
    )

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError(
                "Пароли не совпадают"
            )
        return attrs


class DetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = [
            'email',
            'email_confirmed',
        ]


class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(
        max_length=128,
    )
    new_password = serializers.CharField(
        max_length=128,
    )
    confirm_password = serializers.CharField(
        max_length=128,
    )

    class Meta:
        model = CustomUser
        fields = [
            'old_password',
            'new_password',
            'confirm_password',
        ]

    def validate(self, attrs):
        old_password = attrs.get('old_password')
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')

        if not self.instance.check_password(old_password):
            raise serializers.ValidationError(
                "Старый пароль неверный"
            )
        if new_password != confirm_password:
            raise serializers.ValidationError(
                "Пароли не совпадают"
            )
        return attrs
