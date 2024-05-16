from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from auth.views import LoginView, LogoutView
from youtubedl.viewsets import YoutubeDLViewSet 

router = DefaultRouter()
router.register(r"youtubedl", YoutubeDLViewSet, basename="youtubedl")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("djoser.urls")),
    # path("auth/", include("djoser.urls.jwt")),
    path('auth/jwt/create/', LoginView.as_view(), name='jwt-create'),
    path("auth/logout/", LogoutView.as_view()),
    path("api/", include(router.urls)), 
]