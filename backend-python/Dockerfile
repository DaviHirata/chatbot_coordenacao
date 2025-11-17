# Usar uma imagem base do Python
FROM python:3.11-slim

# Definir o diretório de trabalho no contêiner
WORKDIR /app

# Copiar o arquivo de dependências e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pré-baixar o modelo de embedding para o cache da imagem
COPY download_model.py .
RUN python download_model.py

# Copiar o resto do código da aplicação
COPY . .

# Expor a porta que o FastAPI vai usar
EXPOSE 8001

# Comando para iniciar a aplicação com Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
