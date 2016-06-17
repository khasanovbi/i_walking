from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'password', 'phone', 'vk_profile',
                  'fb_profile', 'avatar')
        extra_kwargs = {
            'vk_profile': {'read_only': True},
            'fb_profile': {'read_only': True},
            'password': {'write_only': True}
        }


class SignUpSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'first_name', 'last_name', 'avatar')
        extra_kwargs = {
            'vk_profile': {'read_only': True},
            'fb_profile': {'read_only': True}
        }

    def create(self, validated_data):
        if validated_data.get('password'):
            validated_data['password'] = make_password(
                validated_data['password']
            )
        return super(SignUpSerializer, self).create(validated_data)


# noinspection PyAbstractClass
class SignInSerializer(serializers.Serializer):
    username = serializers.CharField(label='Юзернейм')
    password = serializers.CharField(style={'input_type': 'password'}, label='Пароль')
