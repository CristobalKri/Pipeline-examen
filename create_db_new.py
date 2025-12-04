import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect('example_new.db')
c = conn.cursor()

c.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
''')

c.execute('''
    INSERT INTO users (username, password, role) VALUES
    (?, ?, 'admin'),
    (?, ?, 'user')
''', (
    'admin', generate_password_hash('password'),
    'user', generate_password_hash('password')
))

c.execute('''
    CREATE TABLE comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        comment TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
''')

conn.commit()
conn.close()

print("Base de datos y tablas creadas con éxito.")
