import sqlite3
import bcrypt

def create_connection():
    """Crear una conexión a la base de datos SQLite."""
    conn = sqlite3.connect('distribuidora_chavez.db')
    return conn

def create_tables():
    """Crear las tablas de productos y usuarios si no existen."""
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT NOT NULL,
            nombre TEXT NOT NULL,
            categoria TEXT NOT NULL,
            precio REAL NOT NULL,
            descripcion TEXT NOT NULL,
            imagen TEXT DEFAULT '/static/uploads/default.jpg'
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
        ''')
    return True

def add_admin_user(username, password):
    """Agregar un usuario administrador."""
    conn = create_connection()
    with conn:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM usuarios WHERE username = ?", (username,))
        user_exists = cursor.fetchone()

        if user_exists:
            print(f"El usuario '{username}' ya existe.")
            return False

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        try:
            cursor.execute(''' 
            INSERT INTO usuarios (username, password)
            VALUES (?, ?)
            ''', (username, hashed_password))
            print(f"Usuario '{username}' creado exitosamente.")
        except sqlite3.Error as e:
            print(f"Error al insertar el usuario '{username}': {e}")
            return False

    return True

if __name__ == "__main__":
    create_tables()