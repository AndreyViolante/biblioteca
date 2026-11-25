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
python manage.py createsuperuser
python manage.py runserver
```

Abra http://127.0.0.1:8000/. Sem `DB_NAME` no `.env`, usa SQLite; com `DB_NAME`
preenchido, usa PostgreSQL.

