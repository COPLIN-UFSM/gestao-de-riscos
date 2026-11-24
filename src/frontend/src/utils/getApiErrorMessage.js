const GENERIC_MESSAGES = {
  login: 'Não foi possível entrar agora. Revise seu SIAPE e sua senha e tente novamente.',
  cadastro: 'Não foi possível concluir o cadastro agora. Revise os dados informados e tente novamente.',
  recuperar_enviar: 'Não foi possível solicitar a recuperação agora. Tente novamente em instantes.',
  recuperar_redefinir: 'Não foi possível redefinir a senha agora. Tente novamente em instantes.',
  default: 'Não foi possível concluir esta ação agora. Tente novamente em instantes.',
};

function normalizeMessage(message) {
  if (!message) {
    return '';
  }

  if (Array.isArray(message)) {
    return message.join(' ');
  }

  if (typeof message === 'object') {
    const values = Object.values(message).flatMap((value) => (Array.isArray(value) ? value : [value]));
    return values.filter(Boolean).join(' ');
  }

  return String(message);
}

export function getApiErrorMessage(error, context = 'default') {
  const status = error?.response?.status;
  const backendMessage = normalizeMessage(error?.response?.data?.erro || error?.response?.data);

  if (backendMessage) {
    return backendMessage;
  }

  if (error?.code === 'ECONNABORTED') {
    return 'A solicitação demorou mais do que o esperado. Tente novamente.';
  }

  if (!error?.response) {
    return 'Não foi possível se comunicar com o servidor. Verifique sua conexão e tente novamente.';
  }

  if (status === 401) {
    return 'Sua sessão expirou ou não é válida para esta ação. Faça login novamente.';
  }

  if (status === 403) {
    return 'Você não tem permissão para executar esta ação.';
  }

  if (status === 404) {
    return 'O recurso solicitado não foi encontrado.';
  }

  if (status >= 500) {
    return 'O servidor encontrou um problema ao processar sua solicitação. Tente novamente em instantes.';
  }

  return GENERIC_MESSAGES[context] || GENERIC_MESSAGES.default;
}
