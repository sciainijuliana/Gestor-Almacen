from conexion import conectar

conn = conectar()
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(materia_prima_stock)")
print(cursor.fetchall())
conn.close()
