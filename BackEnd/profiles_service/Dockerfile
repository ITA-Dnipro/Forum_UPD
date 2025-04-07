FROM python:3.9-alpine

WORKDIR /app

COPY . .

ENV PYTHONPATH=/app

RUN pip install -r requirements.txt

CMD ["python", "main.py" ]