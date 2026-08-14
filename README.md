# Librerias que debes tener instalados

pip install fastapi "uvicorn[standard]" sqlalchemy psycopg2-binary httpx cryptography python-dotenv


# Crear base de datos en postgres
CREATE DATABASE chat_seguro;

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    sender VARCHAR(50) NOT NULL,
    receiver VARCHAR(50) NOT NULL,
    ciphertext TEXT NOT NULL,
    signature TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

# En database.py
- Cambia la variable "TU_PASSWORD" por la contraseña de tu base de datos postgres sql
TU_PASSWORD = "tu_password_de_postgres"


# Abrir 3 terminales
- En terminal 1 (de cia_api.py) ejecutar:
python -m uvicorn cia_api:app --reload --port 8000

- En terminal 2 (de chat_server.py) ejecutar:
python -m uvicorn chat_server:app --reload --port 8001

- En terminal 3 (frintend) ejecutar:
cd frontend
npm run dev

# Final
- Abrir el http://localhost:5173/
