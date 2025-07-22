import psycopg2

try:
    conn = psycopg2.connect(
        dbname="rentacos",
        user="postgres",
        password="26549460",
        host="localhost",
        port="5432"
    )
    print("¡Conexión exitosa!")
    conn.close()
except Exception as e:
    print(f"Error de conexión: {e}")