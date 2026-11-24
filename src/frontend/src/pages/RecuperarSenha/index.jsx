import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ThemeToggle from '../../components/ThemeToggle';
import { useFeedback } from '../../context/FeedbackContext';
import api from '../../services/api';
import { getApiErrorMessage } from '../../utils/getApiErrorMessage';
import './styles.css';

function getResetCredentialsFromUrl() {
  const params = new URLSearchParams(window.location.hash.slice(1));
  const uid = params.get('uid') || '';
  const token = params.get('token') || '';

  return uid && token ? { uid, token } : { uid: '', token: '' };
}

const RecuperarSenha = () => {
  const [email, setEmail] = useState('');
  const [credenciais] = useState(getResetCredentialsFromUrl);
  const [novaSenha, setNovaSenha] = useState('');
  const [confirmacaoSenha, setConfirmacaoSenha] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [linkSolicitado, setLinkSolicitado] = useState(false);
  const navigate = useNavigate();
  const { showFeedback } = useFeedback();
  const linkPresente = Boolean(credenciais.uid && credenciais.token);

  useEffect(() => {
    if (linkPresente) {
      window.history.replaceState(
        window.history.state,
        '',
        window.location.pathname + window.location.search,
      );
    }
  }, [linkPresente]);

  const handleSolicitarLink = async (event) => {
    event.preventDefault();
    setLoading(true);

    try {
      await api.post('/usuarios/recuperar-senha/enviar/', { email });
      setLinkSolicitado(true);
    } catch (error) {
      showFeedback({
        type: 'error',
        title: 'Solicitação não concluída',
        message: getApiErrorMessage(error, 'recuperar_enviar'),
      });
    } finally {
      setLoading(false);
    }
  };

  const handleRedefinirSenha = async (event) => {
    event.preventDefault();

    if (novaSenha !== confirmacaoSenha) {
      showFeedback({
        type: 'warning',
        title: 'Senha divergente',
        message: 'A confirmação deve ser igual à nova senha para continuar.',
      });
      return;
    }

    setLoading(true);
    try {
      await api.post('/usuarios/recuperar-senha/redefinir/', {
        ...credenciais,
        nova_senha: novaSenha,
        confirmacao_senha: confirmacaoSenha,
      });
      showFeedback({
        type: 'success',
        title: 'Senha atualizada',
        message: 'Sua senha foi redefinida. Você será redirecionado para a tela de login.',
      });
      setTimeout(() => navigate('/login'), 1200);
    } catch (error) {
      showFeedback({
        type: 'error',
        title: 'Redefinição não concluída',
        message: getApiErrorMessage(error, 'recuperar_redefinir'),
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="recuperar-container">
      <div className="public-theme-toggle">
        <ThemeToggle />
      </div>

      <main className={`recuperar-card ${linkPresente ? 'redefinir-layout' : ''}`}>
        <div className="recuperar-form-section">
          <header className="recuperar-header">
            <h1 className="recuperar-title-main">Sistema de Gestão de Riscos</h1>
          </header>

          {!linkPresente && (
            <>
              <h2 className="recuperar-subtitle-section">Recuperar acesso</h2>
              {linkSolicitado ? (
                <p className="recuperar-description" role="status">
                  Se o e-mail estiver cadastrado, enviaremos um link de recuperação. Verifique sua caixa
                  de entrada e a pasta de spam.
                </p>
              ) : (
                <>
                  <p className="recuperar-description">
                    Informe o e-mail cadastrado para receber um link seguro de redefinição de senha.
                  </p>
                  <form onSubmit={handleSolicitarLink}>
                    <div className="input-group">
                      <label htmlFor="email">E-mail cadastrado</label>
                      <div className="input-with-icon">
                        <span className="input-icon">
                          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
                        </span>
                        <input
                          type="email"
                          id="email"
                          value={email}
                          onChange={(event) => setEmail(event.target.value)}
                          placeholder="nome@exemplo.com"
                          autoComplete="email"
                          required
                        />
                      </div>
                    </div>
                    <button type="submit" className="recuperar-button" disabled={loading}>
                      {loading ? 'Enviando...' : 'Enviar link de recuperação'}
                    </button>
                  </form>
                </>
              )}
            </>
          )}

          {linkPresente && (
            <>
              <p className="recuperar-title-small" style={{ textAlign: 'left', marginBottom: '8px' }}>SEGURANÇA DA CONTA</p>
              <h2 className="recuperar-subtitle-section" style={{ marginTop: 0, fontSize: '24px' }}>Escolha sua nova senha</h2>
              <p className="recuperar-description">
                O link é temporário e só pode ser usado uma vez. Crie uma senha forte e única.
              </p>

              <form onSubmit={handleRedefinirSenha}>
                <div className="input-group">
                  <label htmlFor="novaSenha">Nova senha</label>
                  <div className="input-with-icon">
                    <span className="input-icon">
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
                    </span>
                    <input
                      type={showPassword ? 'text' : 'password'}
                      id="novaSenha"
                      value={novaSenha}
                      onChange={(event) => setNovaSenha(event.target.value)}
                      autoComplete="new-password"
                      required
                    />
                    <button
                      type="button"
                      className="password-toggle"
                      aria-label={showPassword ? 'Ocultar senha' : 'Mostrar senha'}
                      onClick={() => setShowPassword((visible) => !visible)}
                    >
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
                    </button>
                  </div>
                </div>

                <div className="input-group">
                  <label htmlFor="confirmarSenha">Confirmar nova senha</label>
                  <div className="input-with-icon">
                    <span className="input-icon">
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
                    </span>
                    <input
                      type={showPassword ? 'text' : 'password'}
                      id="confirmarSenha"
                      value={confirmacaoSenha}
                      onChange={(event) => setConfirmacaoSenha(event.target.value)}
                      autoComplete="new-password"
                      required
                    />
                  </div>
                </div>

                <button type="submit" className="recuperar-button" disabled={loading}>
                  {loading ? 'Processando...' : 'Redefinir senha'}
                </button>
              </form>
            </>
          )}

          <div className="back-to-login" onClick={() => navigate('/login')}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="19" y1="12" x2="5" y2="12"></line><polyline points="12 19 5 12 12 5"></polyline></svg>
            Voltar para o login
          </div>
        </div>

        {linkPresente && (
          <div className="recuperar-sidebar-info">
            <h3 className="sidebar-title">Requisitos de senha</h3>
            <ul className="requirements-list">
              <li className={novaSenha.length >= 8 ? 'met' : ''}>Mínimo de 8 caracteres</li>
              <li className={/[A-Z]/.test(novaSenha) ? 'met' : ''}>Pelo menos uma letra maiúscula</li>
              <li className={/[0-9!@#$%^&*]/.test(novaSenha) ? 'met' : ''}>Um número ou símbolo</li>
              <li className={novaSenha && novaSenha !== '12345678' ? 'met' : ''}>Não use a senha padrão</li>
            </ul>
            <div className="tips-box">
              <div>
                <strong>DICAS</strong>
                <p>Evite datas de nascimento ou nomes óbvios. Use uma senha forte.</p>
              </div>
            </div>
          </div>
        )}
      </main>

      <footer className="recuperar-footer-text">
        Sistema institucional de gestão de riscos
      </footer>
    </div>
  );
};

export default RecuperarSenha;
