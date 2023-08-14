FROM python:3

WORKDIR /app
COPY . /app

RUN ls
RUN pip install --no-cache-dir -r /app/requirements.txt

RUN useradd -m myuser
USER myuser
CMD ["NEW_RELIC_CONFIG_FILE=/app/newrelic.ini", "newrelic-admin", "gunicorn", "wsgi:app"]