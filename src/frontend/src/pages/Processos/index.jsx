import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Sidebar from '../../components/Sidebar';
import ThemeToggle from '../../components/ThemeToggle';
import { useAuth } from '../../context/AuthContext';
import { useFeedback } from '../../context/FeedbackContext';
import api from '../../services/api';
import { getApiErrorMessage } from '../../utils/getApiErrorMessage';
import { getSetorLabel } from '../../utils/unidades';
import './styles.css';

const CATEGORIAS = ['Operacional', 'Estratégico', 'Integridade', 'Imagem', 'Financeiro'];

export default function Processos() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { showFeedback } = useFeedback();
  const unidades = user?.setores || [];
  const [macroprocessos, setMacroprocessos] = useState([]);
  const [processos, setProcessos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    nome: '',
    categoria: CATEGORIAS[0],
    macroprocesso: '',
    unidades: unidades[0] ? [String(unidades[0].id)] : [],
  });

  useEffect(() => {
    async function carregarDados() {
      try {
        const [macroRes, processoRes] = await Promise.all([
          api.get('/riscos/macroprocessos/'),
          api.get('/riscos/processos/'),
        ]);
        setMacroprocessos(macroRes.data.results || macroRes.data);
        setProcessos(processoRes.data.results || processoRes.data);
      } catch (err) {
        showFeedback({
          type: 'error',
          title: 'Dados indisponíveis',
          message: getApiErrorMessage(err, 'processos'),
        });
      } finally {
        setLoading(false);
      }
    }
    carregarDados();
  }, [showFeedback]);

  function alterarUnidade(id) {
    setForm((atual) => ({
      ...atual,
      unidades: atual.unidades.includes(id)
        ? atual.unidades.filter((unidadeId) => unidadeId !== id)
        : [...atual.unidades, id],
    }));
  }

  async function criarProcesso(event) {
    event.preventDefault();
    setSaving(true);
    try {
      const response = await api.post('/riscos/processos/', {
        ...form,
        macroprocesso: Number(form.macroprocesso),
        unidades: form.unidades.map(Number),
      });
      setProcessos((anteriores) =>
        [...anteriores, response.data].sort((a, b) => a.nome.localeCompare(b.nome))
      );
      setForm({
        nome: '',
        categoria: CATEGORIAS[0],
        macroprocesso: '',
        unidades: unidades[0] ? [String(unidades[0].id)] : [],
      });
      showFeedback({
        type: 'success',
        title: 'Processo criado',
        message: 'O processo já pode ser associado a riscos das unidades selecionadas.',
      });
    } catch (err) {
      showFeedback({
        type: 'error',
        title: 'Não foi possível criar o processo',
        message: getApiErrorMessage(err, 'processos'),
      });
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="dashboard-container">
      <Sidebar />
      <main className="dashboard-main">
        <header className="dashboard-header">
          <div className="header-title">
            <div className="title-line"></div>
            <h1>Processos</h1>
          </div>
          <div className="header-actions">
            <button className="btn-cancel" type="button" onClick={() => navigate('/planos')}>
              Voltar aos planos
            </button>
            <ThemeToggle compact />
          </div>
        </header>

        <div className="processes-content">
          <section className="processes-card">
            <h2>Cadastrar processo</h2>
            <p>Todo processo deve pertencer a um macroprocesso e a pelo menos uma unidade.</p>
            <form onSubmit={criarProcesso}>
              <div className="form-group">
                <label htmlFor="processo-nome">Nome do processo <span className="required">*</span></label>
                <input
                  id="processo-nome"
                  required
                  maxLength={255}
                  value={form.nome}
                  onChange={(event) => setForm({ ...form, nome: event.target.value })}
                />
              </div>
              <div className="processes-row">
                <div className="form-group">
                  <label htmlFor="processo-categoria">Categoria <span className="required">*</span></label>
                  <select
                    id="processo-categoria"
                    value={form.categoria}
                    onChange={(event) => setForm({ ...form, categoria: event.target.value })}
                  >
                    {CATEGORIAS.map((categoria) => (
                      <option key={categoria} value={categoria}>{categoria}</option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <label htmlFor="processo-macro">Macroprocesso <span className="required">*</span></label>
                  <select
                    id="processo-macro"
                    required
                    value={form.macroprocesso}
                    onChange={(event) => setForm({ ...form, macroprocesso: event.target.value })}
                  >
                    <option value="">Selecione um macroprocesso</option>
                    {macroprocessos.map((macro) => (
                      <option key={macro.id} value={macro.id}>{macro.nome}</option>
                    ))}
                  </select>
                </div>
              </div>
              <fieldset className="processes-units">
                <legend>Unidades que compartilham este processo <span className="required">*</span></legend>
                {unidades.length ? unidades.map((unidade) => (
                  <label key={unidade.id}>
                    <input
                      type="checkbox"
                      checked={form.unidades.includes(String(unidade.id))}
                      onChange={() => alterarUnidade(String(unidade.id))}
                    />
                    {getSetorLabel(unidade)}
                  </label>
                )) : <p>Nenhuma unidade está associada ao seu usuário.</p>}
              </fieldset>
              <button
                className="btn-primary"
                type="submit"
                disabled={saving || loading || !form.unidades.length || !macroprocessos.length}
              >
                {saving ? 'Salvando...' : 'Criar processo'}
              </button>
            </form>
          </section>

          <section className="processes-card">
            <h2>Processos cadastrados</h2>
            {loading ? <p>Carregando processos...</p> : processos.length ? (
              <div className="processes-list">
                {processos.map((processo) => (
                  <article key={processo.id} className="process-item">
                    <div>
                      <strong>{processo.nome}</strong>
                      <span>{processo.categoria} · {processo.macroprocesso_detalhes?.nome}</span>
                      <small>
                        {(processo.unidades || [])
                          .map((id) => unidades.find((unidade) => unidade.id === id))
                          .filter(Boolean)
                          .map(getSetorLabel)
                          .join(', ') || 'Compartilhado com outras unidades'}
                      </small>
                    </div>
                  </article>
                ))}
              </div>
            ) : <p>Nenhum processo cadastrado.</p>}
          </section>
        </div>
      </main>
    </div>
  );
}
