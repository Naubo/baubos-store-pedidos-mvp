# Baubos Store: Pedidos (MVP)

Sistema web para organizar os pedidos de produtos personalizados da Baubos Store, uma loja de Pindamonhangaba (SP). O cliente envia as fotos por um formulário no celular e o sistema gera o PDF pronto para impressão, no layout do kit escolhido (polaroids e bottons).

> Projeto da disciplina de Projeto de Software, do curso de Análise e Desenvolvimento de Sistemas (Cruzeiro do Sul Virtual).
> **Status: em desenvolvimento.** Este README é atualizado conforme o código avança.

## Problema

Hoje cada pedido personalizado leva de 20 a 40 minutos de montagem manual (ajuste de imagem no Canva, impressão e recorte), com risco de foto mal encaixada. As fotos chegam soltas pelo WhatsApp, e pedidos, custos e materiais ficam em planilhas separadas.

## O que o MVP faz

Obrigatórios:

- **RF01**: cadastro, edição e desativação de kits (formato, medidas, fotos por kit, itens por folha).
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
- Bootstrap 5.3

## ODS

ODS 8 (Trabalho Decente e Crescimento Econômico), com foco nas metas 8.2 e 8.3: produtividade com tecnologia e apoio a pequenos negócios.

## Como rodar localmente (em construção)

Os passos abaixo valem quando o código da aplicação estiver no repositório e serão conferidos antes da entrega:

1. Criar e ativar um ambiente virtual com Python 3.12.
2. Instalar as dependências com `pip install -r requirements.txt`.
3. Definir as variáveis de ambiente (nomes previstos: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`). Segredos nunca são enviados ao repositório.
4. Criar as tabelas com `python manage.py migrate`.
5. Criar o usuário do responsável com `python manage.py createsuperuser`.
6. Iniciar com `python manage.py runserver`.

## Estrutura prevista

- `config/`: configurações do projeto Django.
- `pedidos/`: aplicativo principal (models, views, forms e templates).
- `pedidos/arte/`: módulo de geração da arte (Pillow e ReportLab).
- `docs/`: documentação mínima (decisões e protótipo).
- `.github/workflows/`: pipeline de integração contínua.

## Autor

Nauber Gutieres
