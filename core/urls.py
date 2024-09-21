from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from auth.views import LoginView, LogoutView, UserView
from youtubedl.viewsets import YoutubeDLViewSet 
from playlist.viewsets import PlaylistViewSet

router = DefaultRouter()
router.register(r"youtubedl", YoutubeDLViewSet, basename="youtubedl")
router.register(r"playlist", PlaylistViewSet, basename="playlist")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("djoser.urls")),
    # path("auth/", include("djoser.urls.jwt")),
    path('auth/jwt/create/', LoginView.as_view(), name='jwt-create'),
    path("auth/logout/", LogoutView.as_view()),
    path("auth/update/", UserView.as_view(), name='auth-update'),
    path("api/", include(router.urls))
]