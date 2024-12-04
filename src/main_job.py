import os
import pyodbc
from datetime import datetime

# Salva o último timestamp processado
last_processed_timestamp = None

def fetch_data_from_source():
    global last_processed_timestamp

    conn = pyodbc.connect(
        f'DRIVER={{ODBC Driver 17 for SQL Server}};'
        f'SERVER={os.getenv("SOURCE_DB_HOST")};'
        f'DATABASE={os.getenv("SOURCE_DB_NAME")};'
        f'UID={os.getenv("DB_USER")};'
        f'PWD={os.getenv("DB_PASSWORD")};'
    )
    cursor = conn.cursor()

    # Define o filtro para pegar dados novos
    query = "SELECT id, name, updated_at FROM source_table WHERE updated_at > ?"
    params = (last_processed_timestamp,) if last_processed_timestamp else (datetime.min,)
    cursor.execute(query, params)

    for row in cursor:
        yield row

    # Atualiza o último timestamp processado
    last_processed_timestamp = datetime.now()

    conn.close()

# Exemplo do pipeline no Flink
def main():
    from pyflink.datastream import StreamExecutionEnvironment

    env = StreamExecutionEnvironment.get_execution_environment()

    # Fonte: Leia os dados incrementais
    source_stream = env.from_collection(fetch_data_from_source())

    # Transformação: Aqui você pode adicionar lógica
    processed_stream = source_stream.map(lambda record: record)

    # Sink: Escreve no banco de destino
    processed_stream.add_sink(write_to_sink)

    # Executa o job
    env.execute("Incremental Job with Timestamp")

def write_to_sink(record):
    conn = pyodbc.connect(
        f'DRIVER={{ODBC Driver 17 for SQL Server}};'
        f'SERVER={os.getenv("TARGET_DB_HOST")};'
        f'DATABASE={os.getenv("TARGET_DB_NAME")};'
        f'UID={os.getenv("DB_USER")};'
        f'PWD={os.getenv("DB_PASSWORD")};'
    )
    cursor = conn.cursor()
    cursor.execute("INSERT INTO target_table (id, name, updated_at) VALUES (?, ?, ?)", record)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
