import csv
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from src.riscos.models import DesafioPDI, Macroprocesso, ObjetivoPDI


def _ler_csv(caminho, campos_obrigatorios):
    try:
        with caminho.open("r", encoding="utf-8-sig", newline="") as arquivo:
            leitor = csv.DictReader(arquivo)
            cabecalho = leitor.fieldnames or []
            faltantes = [campo for campo in campos_obrigatorios if campo not in cabecalho]
            if faltantes:
                raise CommandError(
                    f"CSV inválido em {caminho}. Campos obrigatórios ausentes: "
                    + ", ".join(faltantes)
                )
            return list(leitor)
    except OSError as exc:
        raise CommandError(f"Não foi possível ler o arquivo {caminho}: {exc}") from exc


def _valor_obrigatorio(linha, campo, numero_linha, caminho):
    valor = (linha.get(campo) or "").strip()
    if not valor:
        raise CommandError(
            f"Valor obrigatório ausente no campo '{campo}', linha {numero_linha} "
            f"do arquivo {caminho}."
        )
    return valor


class Command(BaseCommand):
    help = "Importa ou atualiza desafios, macroprocessos e objetivos do PDI a partir de arquivos CSV."

    def add_arguments(self, parser):
        raiz_projeto = Path(__file__).resolve().parents[4]
        diretorio_padrao = raiz_projeto / "backend" / "database"
        parser.add_argument(
            "--arquivo-desafios",
            default=diretorio_padrao / "desafios_pdi.csv",
            type=Path,
            help="CSV com as colunas numero,descricao.",
        )
        parser.add_argument(
            "--arquivo-objetivos",
            default=diretorio_padrao / "objetivos_pdi.csv",
            type=Path,
            help="CSV com as colunas codigo,descricao,numero_desafio.",
        )
        parser.add_argument(
            "--arquivo-macroprocessos",
            default=diretorio_padrao / "macroprocessos_pdi.csv",
            type=Path,
            help="CSV com a coluna nome.",
        )

    def handle(self, *args, **options):
        caminho_desafios = options["arquivo_desafios"]
        caminho_objetivos = options["arquivo_objetivos"]
        caminho_macroprocessos = options["arquivo_macroprocessos"]
        linhas_desafios = _ler_csv(caminho_desafios, ("numero", "descricao"))
        linhas_objetivos = _ler_csv(
            caminho_objetivos, ("codigo", "descricao", "numero_desafio")
        )
        linhas_macroprocessos = _ler_csv(caminho_macroprocessos, ("nome",))

        desafios = {}
        for numero_linha, linha in enumerate(linhas_desafios, start=2):
            numero_texto = _valor_obrigatorio(
                linha, "numero", numero_linha, caminho_desafios
            )
            try:
                numero = int(numero_texto)
            except ValueError as exc:
                raise CommandError(
                    f"Número de desafio inválido na linha {numero_linha} "
                    f"do arquivo {caminho_desafios}: {numero_texto!r}."
                ) from exc
            if numero in desafios:
                raise CommandError(
                    f"Número de desafio duplicado ({numero}) no arquivo {caminho_desafios}."
                )
            descricao = _valor_obrigatorio(
                linha, "descricao", numero_linha, caminho_desafios
            )
            desafios[numero] = descricao

        objetivos = {}
        for numero_linha, linha in enumerate(linhas_objetivos, start=2):
            codigo = _valor_obrigatorio(
                linha, "codigo", numero_linha, caminho_objetivos
            )
            if codigo in objetivos:
                raise CommandError(
                    f"Código de objetivo duplicado ({codigo}) no arquivo "
                    f"{caminho_objetivos}."
                )
            descricao = _valor_obrigatorio(
                linha, "descricao", numero_linha, caminho_objetivos
            )
            numero_desafio_texto = _valor_obrigatorio(
                linha, "numero_desafio", numero_linha, caminho_objetivos
            )
            try:
                numero_desafio = int(numero_desafio_texto)
            except ValueError as exc:
                raise CommandError(
                    f"Número de desafio inválido na linha {numero_linha} "
                    f"do arquivo {caminho_objetivos}: {numero_desafio_texto!r}."
                ) from exc
            objetivos[codigo] = (descricao, numero_desafio)

        macroprocessos = set()
        for numero_linha, linha in enumerate(linhas_macroprocessos, start=2):
            nome = _valor_obrigatorio(
                linha, "nome", numero_linha, caminho_macroprocessos
            )
            if nome in macroprocessos:
                raise CommandError(
                    f"Macroprocesso duplicado ({nome}) no arquivo "
                    f"{caminho_macroprocessos}."
                )
            macroprocessos.add(nome)

        numeros_desafios_db = set(
            DesafioPDI.all_objects.filter(numero__in=[
                numero for _, numero in objetivos.values()
            ]).values_list("numero", flat=True)
        )
        numeros_desafios_indisponiveis = {
            numero
            for _, numero in objetivos.values()
            if numero not in desafios and numero not in numeros_desafios_db
        }
        if numeros_desafios_indisponiveis:
            raise CommandError(
                "Objetivos referenciam desafios ausentes nos CSVs e no banco: "
                + ", ".join(map(str, sorted(numeros_desafios_indisponiveis)))
            )

        desafios_criados = desafios_atualizados = 0
        macroprocessos_criados = macroprocessos_atualizados = 0
        objetivos_criados = objetivos_atualizados = 0

        with transaction.atomic():
            desafios_por_numero = {}
            for numero, descricao in desafios.items():
                desafio, criado = DesafioPDI.all_objects.update_or_create(
                    numero=numero,
                    defaults={"descricao": descricao, "ativo": True},
                )
                desafios_por_numero[numero] = desafio
                if criado:
                    desafios_criados += 1
                else:
                    desafios_atualizados += 1

            for nome in macroprocessos:
                _, criado = Macroprocesso.all_objects.update_or_create(
                    nome=nome,
                    defaults={"ativo": True},
                )
                if criado:
                    macroprocessos_criados += 1
                else:
                    macroprocessos_atualizados += 1

            if objetivos:
                numeros_objetivos = {
                    numero for _, numero in objetivos.values()
                }
                desafios_por_numero.update(
                    {
                        desafio.numero: desafio
                        for desafio in DesafioPDI.all_objects.filter(
                            numero__in=numeros_objetivos
                        )
                    }
                )

            for codigo, (descricao, numero_desafio) in objetivos.items():
                _, criado = ObjetivoPDI.all_objects.update_or_create(
                    codigo=codigo,
                    defaults={
                        "descricao": descricao,
                        "desafio": desafios_por_numero[numero_desafio],
                        "ativo": True,
                    },
                )
                if criado:
                    objetivos_criados += 1
                else:
                    objetivos_atualizados += 1

        self.stdout.write(
            self.style.SUCCESS(
                "Importação do PDI concluída. "
                f"Desafios criados: {desafios_criados}; atualizados: {desafios_atualizados}. "
                f"Macroprocessos criados: {macroprocessos_criados}; "
                f"atualizados: {macroprocessos_atualizados}. "
                f"Objetivos criados: {objetivos_criados}; atualizados: {objetivos_atualizados}."
            )
        )
