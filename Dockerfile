FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir Flask==3.0.3 gunicorn==22.0.0
COPY . .
ENV DATABASE_PATH=/data/prateleira.db PORT=5000
VOLUME /data
EXPOSE 5000
HEALTHCHECK CMD python -c "import urllib.request;urllib.request.urlopen('http://localhost:5000/health')" || exit 1
CMD ["gunicorn", "-b", "0.0.0.0:5000", "-w", "2", "app:create_app()"]
