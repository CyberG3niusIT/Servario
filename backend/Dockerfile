FROM python:3.12-slim

WORKDIR /app

RUN addgroup --system servario && adduser --system --ingroup servario servario

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chown -R servario:servario /app

USER servario

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
