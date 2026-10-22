from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CsrfTokenView, LoginView, LogoutView, UserViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')

urlpatterns = [
    path('auth/csrf/', CsrfTokenView.as_view(), name='csrf-token'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('', include(router.urls)),
]
