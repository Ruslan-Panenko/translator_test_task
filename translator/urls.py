from django.contrib import admin
from django.urls import path

from firebase.views import TranslationsListAPIView, TranslationDetailAPIView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Swagger Docs",
        default_version='v1',
        description="API description",

    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('translations/', TranslationsListAPIView.as_view()),
    path('translation/<str:pk>', TranslationDetailAPIView.as_view()),
]
