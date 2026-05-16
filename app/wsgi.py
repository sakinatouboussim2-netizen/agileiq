"""WSGI entrypoint utilisé par Gunicorn et la CLI Flask.

- Développement : `flask --app app.wsgi:app run --reload`
- Production    : `gunicorn app.wsgi:app`
"""

from app import create_app

app = create_app()
