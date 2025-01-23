FROM python:3.12-slim
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
RUN addgroup --system app && adduser --system --group app
RUN apt-get update && apt-get install -y libpq-dev gcc postgresql-client iputils-ping
WORKDIR /app
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN mkdir /app/staticfiles
RUN mkdir /app/mediafiles
RUN chmod +x /app/entrypoint.sh
RUN chown -R app:app /app
USER app
EXPOSE 8000
ENTRYPOINT [ "/app/entrypoint.sh" ]  