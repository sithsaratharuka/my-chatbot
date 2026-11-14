FROM python:3.12-slim
WORKDIR /app
COPY requirements_gemini.txt .
RUN pip install --no-cache-dir -r requirements_gemini.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app_gemini:app"]
