FROM python:3

WORKDIR /app
COPY . /app

RUN ls
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

RUN useradd -m myuser
USER myuser
CMD ["gunicorn", "--chdir", "./backend", "-k", "uvicorn.workers.UvicornWorker", "app:app"]