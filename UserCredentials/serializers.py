from rest_framework import serializers

from sampleAppOAuth2.models import TaskChoices, SyncUserTasks
from .models import UserAppCredentials


class UserAppCredentialsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAppCredentials
        fields = '__all__'


class TaskChoicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskChoices
        fields = ("tasks",)


class SyncUserTaskSerializer(serializers.ModelSerializer):
    choices = TaskChoicesSerializer(many=True)

    class Meta:
        model = SyncUserTasks
        fields = ("choices",)
