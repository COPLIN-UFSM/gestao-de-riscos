from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ComentarioMonitoramentoViewSet,
    DesafioPDIViewSet,
    MacroprocessoViewSet,
    MonitoramentoViewSet,
    ObjetivoPDIViewSet,
    PlanoAcaoViewSet,
    ProcessoViewSet,
    RiscoViewSet,
)

router = DefaultRouter()
router.register(r'desafios', DesafioPDIViewSet)
router.register(r'macroprocessos', MacroprocessoViewSet)
router.register(r'processos', ProcessoViewSet)
router.register(r'objetivos', ObjetivoPDIViewSet)
router.register(r'planos', RiscoViewSet)
router.register(r'acoes', PlanoAcaoViewSet)
router.register(r'monitoramentos', MonitoramentoViewSet)
router.register(r'comentarios-monitoramento', ComentarioMonitoramentoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
