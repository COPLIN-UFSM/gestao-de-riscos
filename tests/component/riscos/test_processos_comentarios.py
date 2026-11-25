import pytest
from rest_framework import status

from src.riscos.models import ComentarioMonitoramento, Monitoramento, Processo


@pytest.mark.django_db
class TestProcessoViewSet:
    def test_usuario_autenticado_cria_processo_compartilhado(
        self, api_client, usuario_gestor, setor_oficial, setor_secundario, macroprocesso_padrao
    ):
        api_client.force_authenticate(user=usuario_gestor)

        response = api_client.post(
            "/api/riscos/processos/",
            {
                "nome": "Processo compartilhado via API",
                "categoria": "Operacional",
                "macroprocesso": macroprocesso_padrao.id,
                "unidades": [setor_oficial.id, setor_secundario.id],
            },
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        processo = Processo.objects.get(pk=response.data["id"])
        assert processo.macroprocesso == macroprocesso_padrao
        assert set(processo.unidades.values_list("id", flat=True)) == {
            setor_oficial.id,
            setor_secundario.id,
        }

    def test_filtra_processos_por_unidade(
        self, api_client, usuario_gestor, setor_oficial, setor_secundario, macroprocesso_padrao
    ):
        processo = Processo.objects.create(
            nome="Processo da unidade oficial",
            categoria="Operacional",
            macroprocesso=macroprocesso_padrao,
        )
        processo.unidades.add(setor_oficial)
        api_client.force_authenticate(user=usuario_gestor)

        response = api_client.get(f"/api/riscos/processos/?unidade={setor_secundario.id}")

        assert response.status_code == status.HTTP_200_OK
        assert response.data == []


@pytest.mark.django_db
class TestComentarioMonitoramentoViewSet:
    def test_qualquer_usuario_autenticado_pode_comentar_e_autoria_nao_e_informada(
        self, api_client, risco_basico, usuario_gestor, usuario_outro_setor
    ):
        monitoramento = Monitoramento.objects.create(
            risco=risco_basico,
            resultados="Resultado",
            acoes_futuras="Ações",
            analise_critica="Análise",
        )
        api_client.force_authenticate(user=usuario_outro_setor)

        response = api_client.post(
            "/api/riscos/comentarios-monitoramento/",
            {
                "monitoramento": monitoramento.id,
                "usuario": usuario_gestor.id,
                "comentario": "Comentário de outra unidade",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        comentario = ComentarioMonitoramento.objects.get(pk=response.data["id"])
        assert comentario.usuario == usuario_outro_setor
        assert comentario.monitoramento == monitoramento
