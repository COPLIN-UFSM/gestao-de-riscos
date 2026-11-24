from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    LoginView,
    RedefinirSenhaView,
    RegistroUsuarioView,
    SetorViewSet,
    SolicitarRedefinicaoSenhaView,
    UsuarioLogadoView,
    UsuarioViewSet,
)

router = DefaultRouter()
router.register(r'setores', SetorViewSet)
router.register(r'gestores', UsuarioViewSet, basename='gestores')

urlpatterns = [
    path('', include(router.urls)),
    path('registro/', RegistroUsuarioView.as_view(), name='registro'),
    path('login/', LoginView.as_view(), name='login'),
    path('me/', UsuarioLogadoView.as_view(), name='usuario-logado'),
    path('recuperar-senha/enviar/', SolicitarRedefinicaoSenhaView.as_view(), name='recuperar_senha_enviar'),
    path('recuperar-senha/redefinir/', RedefinirSenhaView.as_view(), name='recuperar_senha_redefinir'),
]
