FROM python:3.12-slim 

RUN pip install --no-cache-dir poetry==2.5.1 "poetry-plugin-pypi-mirror>=0.6.4"

WORKDIR /app

COPY pyproject.toml poetry.lock ./

ENV POETRY_PYPI_MIRROR_URL=https://pypi-mirror.gitverse.ru/simple/
RUN poetry config virtualenvs.create false && poetry install --only main --no-root

RUN groupadd --gid 1000 app && useradd --uid 1000 --gid app --create-home app

COPY --chown=app:app app ./app
COPY --chown=app:app alembic ./alembic
COPY --chown=app:app alembic.ini ./alembic.ini
COPY --chown=app:app scripts ./scripts
COPY --chown=app:app entrypoint.sh ./entrypoint.sh
COPY --chown=app:app --chmod=755 entrypoint.sh ./entrypoint.sh

USER app

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]