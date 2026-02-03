FROM python:3.12
WORKDIR /app
RUN python -m pip install --upgrade pip
RUN pip install setuptools
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
COPY . .
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "yacut:asgi_app"]