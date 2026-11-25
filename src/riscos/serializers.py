from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from src.usuarios.models import Setor
from src.usuarios.serializers import UnidadeOrganizacionalSerializer

from .models import (
    ComentarioMonitoramento,
    DesafioPDI,
    HistoricoPlano,
    Macroprocesso,
    Monitoramento,
    ObjetivoPDI,
    PlanoAcao,
    Processo,
    Risco,
)


class DesafioPDISerializer(serializers.ModelSerializer):
    class Meta:
        model = DesafioPDI
        fields = '__all__'

class MacroprocessoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Macroprocesso
        fields = '__all__'


class ProcessoSerializer(serializers.ModelSerializer):
    macroprocesso_detalhes = MacroprocessoSerializer(source='macroprocesso', read_only=True)
    unidades = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Setor.objects.all(),
        required=True,
        allow_empty=False,
    )

    class Meta:
        model = Processo
        fields = [
            'id', 'nome', 'categoria', 'macroprocesso', 'macroprocesso_detalhes',
            'unidades', 'ativo',
        ]
        read_only_fields = ['ativo']


class ProcessoDetalhesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Processo
        fields = ['id', 'nome', 'categoria']


class ObjetivoPDISerializer(serializers.ModelSerializer):
    desafio_detalhes = DesafioPDISerializer(source='desafio', read_only=True)
    
    class Meta:
        model = ObjetivoPDI
        fields = ['id', 'codigo', 'descricao', 'desafio', 'desafio_detalhes']

class RiscoSerializer(serializers.ModelSerializer):
    macroprocesso = serializers.PrimaryKeyRelatedField(
        queryset=Macroprocesso.objects.all(),
        required=False,
    )
    processo = serializers.PrimaryKeyRelatedField(
        queryset=Processo.objects.all(),
        required=False,
        allow_null=True,
    )
    processo_detalhes = ProcessoDetalhesSerializer(source='processo', read_only=True)
    nivel_risco = serializers.IntegerField(read_only=True)
    nivel_residual = serializers.IntegerField(read_only=True)
    setor_detalhes = UnidadeOrganizacionalSerializer(source='setor', read_only=True)
    objetivo_detalhes = ObjetivoPDISerializer(source='objetivo', read_only=True)
    macroprocesso_detalhes = MacroprocessoSerializer(source='macroprocesso', read_only=True)
    periodo_acao = serializers.SerializerMethodField()
    possui_plano_acao = serializers.SerializerMethodField()
    possui_monitoramento = serializers.SerializerMethodField()

    class Meta:
        model = Risco
        fields = [
            'uuid', 'setor', 'setor_detalhes', 'objetivo', 'objetivo_detalhes',
            'macroprocesso', 'macroprocesso_detalhes', 'processo', 'processo_detalhes',
            'categoria', 'evento',
            'causa', 'consequencia', 'controles_atuais', 'eficacia_controle',
            'probabilidade', 'impacto', 'nivel_risco', 'prob_residual',
            'imp_residual', 'nivel_residual',
            'periodo_acao', 'possui_plano_acao', 'possui_monitoramento',
        ]

    def get_periodo_acao(self, obj):
        acao = next(iter(obj.planos_acao.all()), None)
        if not acao:
            return {"data_inicio": None, "data_fim": None}
        return {
            "data_inicio": acao.data_inicio.isoformat(),
            "data_fim": acao.data_fim.isoformat(),
        }

    def get_possui_plano_acao(self, obj):
        return any(True for _ in obj.planos_acao.all())

    def get_possui_monitoramento(self, obj):
        return any(True for _ in obj.monitoramentos.all())

    def validate(self, data):
        processo = data.get('processo', getattr(self.instance, 'processo', None))
        macroprocesso = data.get('macroprocesso')
        if processo is not None:
            data['macroprocesso'] = processo.macroprocesso
            setor = data.get('setor', getattr(self.instance, 'setor', None))
            if setor is not None and not processo.unidades.filter(pk=setor.pk).exists():
                raise ValidationError({
                    'processo': "O processo selecionado não está associado à unidade do risco."
                })
        elif macroprocesso is None and (
            self.instance is None or 'processo' in data
        ):
            raise ValidationError({
                'macroprocesso': "Informe um macroprocesso quando nenhum processo for selecionado."
            })

        campos_escala = ['probabilidade', 'impacto', 'prob_residual', 'imp_residual']
        erros = {}
        for campo in campos_escala:
            valor = data.get(campo)
            if valor is not None and not 1 <= valor <= 5:
                erros[campo] = "O valor deve estar entre 1 e 5."
        if erros:
            raise ValidationError(erros)
        return data

class PlanoAcaoSerializer(serializers.ModelSerializer):
    risco = serializers.SlugRelatedField(slug_field='uuid', queryset=Risco.objects.all())

    class Meta:
        model = PlanoAcao
        fields = '__all__'

class MonitoramentoSerializer(serializers.ModelSerializer):
    risco = serializers.SlugRelatedField(slug_field='uuid', queryset=Risco.objects.all())

    class Meta:
        model = Monitoramento
        fields = '__all__'


class ComentarioMonitoramentoSerializer(serializers.ModelSerializer):
    usuario_nome = serializers.CharField(source='usuario.nome', read_only=True)

    class Meta:
        model = ComentarioMonitoramento
        fields = ['id', 'monitoramento', 'usuario', 'usuario_nome', 'comentario', 'data_hora']
        read_only_fields = ['id', 'usuario', 'usuario_nome', 'data_hora']


class HistoricoPlanoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricoPlano
        fields = ['id', 'usuario_nome', 'data_hora', 'descricao']
        read_only_fields = ['id', 'data_hora']
