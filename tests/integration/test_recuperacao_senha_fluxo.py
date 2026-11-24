from urllib.parse import parse_qs, urlparse

import pytest
from django.core import mail
from rest_framework import status


@pytest.mark.django_db
def test_fluxo_completo_de_recuperacao_por_link(api_client, usuario_gestor):
    envio_response = api_client.post(
        "/api/usuarios/recuperar-senha/enviar/",
        {"email": usuario_gestor.email},
        format="json",
    )
    assert envio_response.status_code == status.HTTP_200_OK
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == [usuario_gestor.email]

    link = next(line for line in mail.outbox[0].body.splitlines() if line.startswith("http"))
    credentials = parse_qs(urlparse(link).fragment)
    redefinir_response = api_client.post(
        "/api/usuarios/recuperar-senha/redefinir/",
        {
            "uid": credentials["uid"][0],
            "token": credentials["token"][0],
            "nova_senha": "SenhaNova!Forte8472",
            "confirmacao_senha": "SenhaNova!Forte8472",
        },
        format="json",
    )
    assert redefinir_response.status_code == status.HTTP_200_OK

    login_response = api_client.post(
        "/api/usuarios/login/",
        {"siape": usuario_gestor.siape, "senha": "SenhaNova!Forte8472"},
        format="json",
    )
    assert login_response.status_code == status.HTTP_200_OK
    assert "token" in login_response.data
