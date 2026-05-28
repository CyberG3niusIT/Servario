FROM python:3.12-slim

WORKDIR /app

RUN addgroup --system servario && adduser --system --ingroup servario servario

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chown -R servario:servario /app && chmod +x /app/start.sh

USER servario

EXPOSE 8000

CMD ["sh", "/app/start.sh"]
