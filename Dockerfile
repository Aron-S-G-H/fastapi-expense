FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV SQLALCHEMY_DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/postgres
ENV SECRET_KEY=71259363618141a63865be1a04be41383ce01576e6b20622ec76300caaf13e5d
ENV ALGORITHM=HS256
ENV AUTH_MODE=Bearer
ENV SUPPORTED_LANGS=fa,en
ENV DEFAULT_LANG=en
ENV REDIS_URL=redis://redis:6379 

WORKDIR /usr/src

COPY ./requirements.txt .

RUN pip install --upgrade pip
RUN pip install -i https://mirror-pypi.runflare.com/simple --no-cache-dir --upgrade -r ./requirements.txt

COPY ./src .

EXPOSE 8000

COPY entrypoint.sh /src/entrypoint.sh
RUN chmod +x /src/entrypoint.sh

CMD ["/src/entrypoint.sh"]

# CMD ["fastapi", "dev","--host","0.0.0.0","--port","8000"]