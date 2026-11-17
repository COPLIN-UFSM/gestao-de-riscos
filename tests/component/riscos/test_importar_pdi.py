import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from src.riscos.models import DesafioPDI, ObjetivoPDI


@pytest.mark.django_db
class TestImportarPDI:
    def test_importa_csvs_padrao(self):
        call_command("importar_pdi")

        assert DesafioPDI.objects.count() == 7
        assert ObjetivoPDI.objects.count() == 43

    def test_importa_e_atualiza_desafios_e_objetivos(self, tmp_path):
        caminho_desafios = tmp_path / "desafios.csv"
        caminho_objetivos = tmp_path / "objetivos.csv"
        caminho_desafios.write_text(
            "numero,descricao\n99,Desafio de teste\n",
            encoding="utf-8",
        )
        caminho_objetivos.write_text(
            "codigo,descricao,numero_desafio\n"
            "TEST-99,\"Objetivo de teste, com vírgula\",99\n",
            encoding="utf-8",
        )
        argumentos = {
            "arquivo_desafios": caminho_desafios,
            "arquivo_objetivos": caminho_objetivos,
        }

        call_command("importar_pdi", **argumentos)
        caminho_desafios.write_text(
            "numero,descricao\n99,Desafio atualizado\n",
            encoding="utf-8",
        )
        caminho_objetivos.write_text(
            "codigo,descricao,numero_desafio\nTEST-99,Objetivo atualizado,99\n",
            encoding="utf-8",
        )
        call_command("importar_pdi", **argumentos)

        desafio = DesafioPDI.objects.get(numero=99)
        objetivo = ObjetivoPDI.objects.get(codigo="TEST-99")
        assert desafio.descricao == "Desafio atualizado"
        assert objetivo.descricao == "Objetivo atualizado"
        assert objetivo.desafio == desafio
        assert DesafioPDI.objects.filter(numero=99).count() == 1
        assert ObjetivoPDI.objects.filter(codigo="TEST-99").count() == 1

    def test_rejeita_objetivo_com_desafio_inexistente(self, tmp_path):
        caminho_desafios = tmp_path / "desafios.csv"
        caminho_objetivos = tmp_path / "objetivos.csv"
        caminho_desafios.write_text("numero,descricao\n99,Teste\n", encoding="utf-8")
        caminho_objetivos.write_text(
            "codigo,descricao,numero_desafio\nTEST-100,Objetivo inválido,100\n",
            encoding="utf-8",
        )

        with pytest.raises(CommandError, match="desafios ausentes"):
            call_command(
                "importar_pdi",
                arquivo_desafios=caminho_desafios,
                arquivo_objetivos=caminho_objetivos,
            )

        assert not DesafioPDI.objects.filter(numero=99).exists()
