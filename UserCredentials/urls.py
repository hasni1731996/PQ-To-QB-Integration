from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^save-credentials/$', views.SaveUserCredentials.as_view()),
    url(r'^save-sync-choices/$', views.SaveUserSyncTasksChoices.as_view()),
]
