FROM python:3.8-slim

# Instale dependências do sistema necessárias para pyodbc
RUN apt-get update && apt-get install -y \
    unixodbc \
    unixodbc-dev \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Crie um diretório de trabalho
WORKDIR /app

# Copie o arquivo de dependências e instale as bibliotecas Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie o restante dos arquivos do projeto
COPY . .

# Defina o comando padrão para executar o job
CMD ["python", "src/main_job.py"]
