from django.urls import path, include
from cas import views

urlpatterns = [
  path("documents/", views.DocumentList.as_view(), name='documents' ),
  path("summaries/", views.SummaryList.as_view(), name='summaries' ),
  path("upload/", views.upload, name='upload' ),
]
