from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('entrar/', LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('sair/', LogoutView.as_view(), name='logout'),
    path('', include('acervo.urls')),
]
