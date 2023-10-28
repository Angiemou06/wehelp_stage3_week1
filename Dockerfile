FROM python:3-alpine3.16
FROM --platform=linux/amd64 python:3.8


WORKDIR /app
COPY . /app
COPY static /app/static
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "app.py"]



