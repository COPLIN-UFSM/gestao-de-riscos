FROM python:3.11-slim

LABEL authors="henryzord"
LABEL name="gestao-de-riscos"
LABEL description="Backend Django do sistema Gestão de Riscos UFSM"
LABEL version="1.0"

WORKDIR /home

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libgraphviz-dev \
    libxml2 \
    locales \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DJANGO_SETTINGS_MODULE=src.gestao_risco.settings.production

EXPOSE 8000

CMD ["gunicorn", "src.gestao_risco.wsgi:application", "--bind", "0.0.0.0:8000"]