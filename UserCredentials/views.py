from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from UserCredentials.models import UserAppCredentials
from UserCredentials.serializers import UserAppCredentialsSerializer, SyncUserTaskSerializer
from sampleAppOAuth2.models import SyncUserTasks, TaskChoices


class SaveUserCredentials(APIView):
    """
        Save User Credentials for both Sandbox & Production
        {
            "sandbox_procore_app_id":"ddhdhdhd",
            "sandbox_procore_app_secret":"dhdhdhdhd",
            "sandbox_procore_redirect_url":"djjdjdjd",
            "sandbox_qbo_app_id":"dsdsds",
            "sandbox_qbo_app_secret":"dsdsdsdsd",
            "sandbox_qbo_redirect_url":"dsdsdss",
            "is_sandbox_active":true
        }

    """

    def get(self, request):
        try:
            user_credentials = UserAppCredentials.objects.get(user=self.request.user.id)
            serializer = UserAppCredentialsSerializer(user_credentials)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({"credentials_exists": False}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        try:
            data = request.data
            data['user'] = self.request.user.id
            serializer = UserAppCredentialsSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"Error": str(e)})

    def put(self, request):
        try:
            obj = UserAppCredentials.objects.get(id=request.data["id"])
            serializer = UserAppCredentialsSerializer(obj, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"Error": str(e)})


class SaveUserSyncTasksChoices(APIView):
    """
        Choices can be as follows =>
            SYNC_PROJECT_CHOICE_KEY = 1
            SYNC_VENDOR_CHOICE_KEY = 2
            SYNC_COST_CODE_CHOICE_KEY = 3
            SYNC_CUSTOMER_INVOICES_CHOICE_KEY = 4
            SYNC_SUB_CONTRACTOR_INVOICES_CHOICE_KEY = 5
            SYNC_CUSTOMER_PAYMENTS_CHOICE_KEY = 6
            SYNC_SUB_CONTRACTOR_PAYMENTS_CHOICE_KEY = 7
            SYNC_EXPENSE_CHOICE_KEY = 8
        Dummy request data as follows:
        [1,2,3]
    """

    def get(self, request):
        try:
            obj_ = SyncUserTasks.objects.get(user_id=request.user.id)
            serializer = SyncUserTaskSerializer(obj_)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"Object Not Exists..!!": False}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        try:
            sync_user_ = SyncUserTasks.objects.create(user_id=self.request.user.id)
            for obj in request.data:
                task_choice = TaskChoices.objects.get(id=obj)
                sync_user_.choices.add(task_choice)
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"Error": str(e)})
