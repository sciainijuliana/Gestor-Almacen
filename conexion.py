import sqlite3

def conectar():
    conn = sqlite3.connect("almacen.db")
    return conn

def inicializar_bd():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY,
        codigo TEXT,
        nombre TEXT,
        precio REAL,
        stock INTEGER,
        tipo TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY,
        fecha TEXT,
        total REAL,
        metodo_pago TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS detalle_ticket (
        id INTEGER PRIMARY KEY,
        ticket_id INTEGER,
        producto_id INTEGER,
        cantidad INTEGER,
        subtotal REAL,
        tipo TEXT,
        FOREIGN KEY(ticket_id) REFERENCES tickets(id),
        FOREIGN KEY(producto_id) REFERENCES productos(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS recetas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT UNIQUE,
        nombre TEXT,
        tipo TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS receta_detalle (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        receta_id INTEGER,
        codigo_materia TEXT,
        cantidad REAL,
        FOREIGN KEY(receta_id) REFERENCES recetas(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS materia_prima_stock (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT UNIQUE,
        nombre TEXT,
        tipo TEXT,
        cantidad REAL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS produccion_stock (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT UNIQUE,
        nombre TEXT,
        cantidad REAL,
        tipo TEXT
    )
    ''')

    conn.commit()
    conn.close()
