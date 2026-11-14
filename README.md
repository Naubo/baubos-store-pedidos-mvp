# Baubos Store: Pedidos (MVP)

Sistema web para organizar os pedidos de produtos personalizados da Baubos Store, uma loja de Pindamonhangaba (SP). O cliente envia as fotos por um formulário no celular e o sistema gera o PDF pronto para impressão, no layout do kit escolhido (polaroids e bottons).

> Projeto da disciplina de Projeto de Software, do curso de Análise e Desenvolvimento de Sistemas (Cruzeiro do Sul Virtual).
> **Status: MVP com RF01 a RF05 implementados.** RF06 e RF07 ficam para a próxima versão.

## Problema

Hoje cada pedido personalizado leva de 20 a 40 minutos de montagem manual (ajuste de imagem no Canva, impressão e recorte), com risco de foto mal encaixada. As fotos chegam soltas pelo WhatsApp, e pedidos, custos e materiais ficam em planilhas separadas.

## O que o MVP faz

Obrigatórios:

- **RF01**: cadastro, edição e desativação de kits (formato, medidas, fotos por kit, itens por folha), feito pelo painel administrativo do Django (`/admin/`).
- **RF02**: formulário público de pedido, em que o cliente escolhe o kit, envia as fotos e aceita o uso delas.
- **RF03**: geração do PDF em A4 com as fotos nas posições do layout e guias de corte.
- **RF04**: painel do responsável com a lista de pedidos, filtro por status e download do PDF.
- **RF05**: mudança de status do pedido (recebido, em produção, pronto, enviado), sempre em ordem.

Desejáveis (podem ficar para uma próxima versão):

- **RF06**: baixa automática do papel e alerta de saldo baixo.
- **RF07**: limpeza das fotos e PDFs de pedidos já enviados.

## Tecnologias

- Python 3.12
- Django 5.2 LTS (padrão MVT)
- SQLite
- Pillow (tratamento das fotos) e ReportLab (geração do PDF)
- HTML e CSS próprios (mobile primeiro, sem biblioteca externa)

## ODS

ODS 8 (Trabalho Decente e Crescimento Econômico), com foco nas metas 8.2 e 8.3: produtividade com tecnologia e apoio a pequenos negócios.

## Como rodar localmente

Precisa do Python 3.12 instalado. No terminal, dentro da pasta do projeto (exemplo para Windows/PowerShell):

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
$env:DJANGO_DEBUG = "1"
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

No Linux/macOS, use `source .venv/bin/activate` e `export DJANGO_DEBUG=1`. A senha do usuário precisa ter pelo menos 12 caracteres.

Depois disso:

1. Entre em `http://127.0.0.1:8000/admin/` (o login passa pela tela `/entrar/`) e cadastre pelo menos um kit em **Produtos** (formato, medidas em mm, fotos por kit e itens por folha).
2. O formulário do cliente fica em `http://127.0.0.1:8000/` e o painel do responsável em `/painel/`.

Variáveis de ambiente: `DJANGO_SECRET_KEY` (obrigatória fora do modo DEBUG), `DJANGO_DEBUG` (`1` liga o modo de desenvolvimento) e `DJANGO_ALLOWED_HOSTS` (lista separada por vírgulas). Segredos nunca são enviados ao repositório.

## Testes

```
python manage.py test
coverage run manage.py test
coverage report
```

O mesmo comando roda automaticamente no GitHub Actions (`.github/workflows/ci.yml`) a cada push e Pull Request.

## Estrutura

- `config/`: configurações do projeto Django.
- `pedidos/`: aplicativo principal (models, views, forms, templates e testes em `pedidos/tests/`).
- `pedidos/arte/`: tratamento das fotos (`fotos.py`), grade da folha A4 (`layout.py`) e geração do PDF (`pdf.py`).
- `.github/workflows/`: pipeline de integração contínua.

## Autor

Nauber Gutieres
