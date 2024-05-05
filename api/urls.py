from django.urls import path

from rest_framework.authtoken.views import ObtainAuthToken

from . import views

urlpatterns = [
    
    path("api/v1/admin/", views.AdminView.as_view()),

    path("api/v1/token/", ObtainAuthToken.as_view()),
    path("api/v1/users/", views.ServiceAdvisorView.as_view()),
    path("api/v1/users/<int:pk>/", views.ServiceAdvisorManageView.as_view()),
    path("api/v1/jobcards/", views.JobCardView.as_view()),
    path("api/v1/jobcards/<int:pk>/", views.JobCardManageView.as_view()),
    path("api/v1/jobcard/<int:pk>/jobs/", views.JobView.as_view()),
    path("api/v1/jobcard/jobs/<int:pk>/", views.JobManageView.as_view()),
    path("api/v1/jobcard/summary/<int:pk>/", views.JobCardSummaryView.as_view()),

]
