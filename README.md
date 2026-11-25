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
