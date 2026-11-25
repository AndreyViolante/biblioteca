# Biblioteca: mini-SaaS em Django

Sistema de biblioteca para várias organizações na mesma base, com perfis de
acesso, dashboard e API REST. Disciplina: Laboratório de Programação Full Stack.

## Como rodar

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py popular_demo
python manage.py createsuperuser
python manage.py runserver
```

Abra http://127.0.0.1:8000/. Sem `DB_NAME` no `.env`, usa SQLite; com `DB_NAME`
preenchido, usa PostgreSQL.

Usuários de demonstração (a senha está em `acervo/management/commands/popular_demo.py`):

| Usuário | Organização | Papel |
|---|---|---|
| ana | Biblioteca Central | Administrador |
| carla | Biblioteca Central | Operador |
| bruno | Biblioteca do Bairro | Administrador |

Organizações e perfis novos são criados no Admin (`/admin/`, com o superusuário).

## Os quatro pilares da P2

| Pilar | Onde está |
|---|---|
| Multi-organização | `core/models.py` (Organizacao, base DaOrganizacao), `core/acesso.py` (org_atual) |
| Perfis de acesso | `core/models.py` (Perfil), `core/acesso.py` (telas), `core/permissions.py` (API) |
| Dashboard | `acervo/dashboard.py` (métricas), `templates/acervo/dashboard.html`, `static/js/dashboard.js` |
| API REST | `acervo/serializers.py`, `acervo/api_views.py`, `acervo/api_urls.py` |

### Migração em três etapas

A organização entrou em tabelas que já existiam, sem perder registros:
`0006_organizacao_nula` (FK nula), `0007_organizacao_padrao` (RunPython preenche) e
`0008_organizacao_obrigatoria` (FK obrigatória). Conferido em `acervo/tests/test_migracao.py`.

### Papéis

| Ação | Administrador | Operador |
|---|---|---|
| Ver acervo, leitores e empréstimos | Sim | Sim |
| Emprestar e devolver | Sim | Sim |
| Cadastrar e editar leitores | Sim | Sim |
| Cadastrar livros, categorias e autores | Sim | Não |
| Excluir registros | Sim | Não |
| Série por mês e exportação CSV | Sim | Não |

### Regras do empréstimo

Ficam em `Emprestimo.clean()` e valem no Admin, nas telas e na API:
precisa haver exemplar disponível; o leitor deve estar ativo, sem atraso, com menos
de 3 empréstimos abertos e sem o mesmo livro em mãos.

### API

`/api/livros/`, `/api/categorias/`, `/api/autores/`, `/api/leitores/`,
`/api/emprestimos/`, `POST /api/emprestimos/<id>/devolver/` e
`/api/dashboard/?inicio=AAAA-MM-DD&fim=AAAA-MM-DD`.
Autenticação por sessão (login em `/entrar/` ou `/api-auth/login/`).
