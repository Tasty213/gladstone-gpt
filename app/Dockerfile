FROM python:3.11.4

ARG settings_filepath

ENV SETTINGS_FILEPATH=${settings_filepath}

WORKDIR /app
COPY . /app

RUN ls
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

RUN useradd -m myuser
USER myuser
CMD ["gunicorn", "--chdir", "./backend", "-k", "uvicorn.workers.UvicornWorker", "app:app"]