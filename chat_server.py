from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import SessionLocal, engine
from models import Base, Message

import requests


# ============================================================
# CREAR LAS TABLAS
# ============================================================

Base.metadata.create_all(bind=engine)


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="Chat Seguro",
    description="Backend del Chat Seguro basado en la CIA Triad",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

# React corre en http://localhost:5173
# Nuestro backend corre en http://127.0.0.1:8001
#
# Por eso permitimos que React pueda comunicarse
# con este backend mediante HTTP.

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# CIA API
# ============================================================

# La CIA API está ejecutándose en el puerto 8000.
#
# cia_api.py
# http://127.0.0.1:8000

CIA_API_URL = "http://127.0.0.1:8000"


# ============================================================
# MODELO PARA RECIBIR UN MENSAJE
# ============================================================

class SendMessageRequest(BaseModel):

    sender: str
    receiver: str
    message: str


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "message": "Chat Seguro Backend funcionando",
        "frontend": "http://localhost:5173",
        "docs": "http://127.0.0.1:8001/docs"
    }


# ============================================================
# ENVIAR MENSAJE
# ============================================================

@app.post("/messages")
def send_message(payload: SendMessageRequest):

    # ========================================================
    # 1. CIFRAR EL MENSAJE
    # ========================================================
    #
    # Aquí chat_server.py llama a:
    #
    # POST http://127.0.0.1:8000/confidentiality/encrypt
    #
    # que pertenece a cia_api.py
    #

    # ========================================================
    # 1. CIFRAR EL MENSAJE
    # ========================================================
    # Se envía el mensaje a la CIA API mediante HTTP.
    # La CIA API ejecuta el cifrado utilizando Fernet.
    #
    # POST /confidentiality/encrypt  solicita a cia_api.py que lo encripte
    encrypt_response = requests.post(
        f"{CIA_API_URL}/confidentiality/encrypt",
        json={
            "message": payload.message
        }
    )


    if encrypt_response.status_code != 200:

        raise HTTPException(
            status_code=500,
            detail="No se pudo cifrar el mensaje"
        )


    ciphertext = encrypt_response.json()["ciphertext"]


    # ========================================================
    # 2. FIRMAR EL MENSAJE
    # ========================================================
    #
    # POST /integrity/sign
    #

    sign_response = requests.post(
        f"{CIA_API_URL}/integrity/sign",
        json={
            "message": payload.message
        }
    )


    if sign_response.status_code != 200:

        raise HTTPException(
            status_code=500,
            detail="No se pudo firmar el mensaje"
        )


    signature = sign_response.json()["signature"]


    # ========================================================
    # 3. GUARDAR EN POSTGRESQL
    # ========================================================

    db: Session = SessionLocal()


    try:

        new_message = Message(

            sender=payload.sender,

            receiver=payload.receiver,

            ciphertext=ciphertext,

            signature=signature

        )


        db.add(new_message)

        db.commit()

        db.refresh(new_message)


        return {

            "message": "Mensaje enviado correctamente",

            "id": new_message.id

        }


    except Exception as error:

        db.rollback()

        raise HTTPException(

            status_code=500,

            detail=f"Error al guardar el mensaje: {error}"

        )


    finally:

        db.close()


# ============================================================
# OBTENER MENSAJES
# ============================================================

@app.get("/messages")
def get_messages():

    db: Session = SessionLocal()


    try:

        # ====================================================
        # OBTENER MENSAJES DESDE POSTGRESQL
        # ====================================================

        messages = (
            db.query(Message)
            .order_by(Message.created_at.asc())
            .all()
        )


        result = []


        for message in messages:


            # =================================================
            # 4. DESCIFRAR
            # =================================================
            #
            # PostgreSQL contiene ciphertext.
            #
            # Aquí lo mandamos a la CIA API para obtener
            # nuevamente el texto original.
            #

            decrypt_response = requests.post(

                f"{CIA_API_URL}/confidentiality/decrypt",

                json={
                    "ciphertext": message.ciphertext
                }

            )


            if decrypt_response.status_code == 200:

                plaintext = (
                    decrypt_response
                    .json()["plaintext"]
                )

            else:

                print("ERROR CIA API:") ###
                print("Status:", decrypt_response.status_code) ###
                print("Respuesta:", decrypt_response.text) ##borra

                plaintext = "[ERROR: No se pudo descifrar]"


            # =================================================
            # 5. ESTADO DE VERIFICACIÓN
            # =================================================

            verification_status = "No verificado"


            # =================================================
            # 6. VERIFICAR INTEGRIDAD
            # =================================================
            #
            # Mandamos:
            #
            # mensaje original
            # +
            # firma almacenada
            #
            # a la CIA API.
            #

            verify_response = requests.post(

                f"{CIA_API_URL}/integrity/verify",

                json={

                    "message": plaintext,

                    "signature": message.signature

                }

            )


            if verify_response.status_code == 200:

                valid = (
                    verify_response
                    .json()["valid"]
                )


                if valid:

                    verification_status = (
                        "Mensaje verificado"
                    )

                else:

                    verification_status = (
                        "Integridad comprometida"
                    )


            # =================================================
            # 7. PREPARAR RESPUESTA PARA REACT
            # =================================================

            result.append({

                "id": message.id,

                "sender": message.sender,

                "receiver": message.receiver,

                "message": plaintext,

                "timestamp": message.created_at,

                "verification": verification_status

            })


        return result


    finally:

        db.close()