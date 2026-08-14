import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8001";

function App() {

    const [messages, setMessages] = useState([]);

    const [sender, setSender] = useState("Usuario A");

    const [receiver, setReceiver] = useState("Usuario B");

    const [message, setMessage] = useState("");

    const [status, setStatus] = useState(
        "Conectando con el servidor..."
    );


    // ========================================================
    // CARGAR MENSAJES
    // ========================================================

    const loadMessages = async () => {

        try {

            const response = await fetch(
                `${API_URL}/messages`
            );

            if (!response.ok) {
                throw new Error(
                    "Error al obtener los mensajes"
                );
            }

            const data = await response.json();

            setMessages(data);

            setStatus(
                "Conectado — mensajes cargados desde PostgreSQL"
            );

        } catch (error) {

            console.error(error);

            setStatus(
                "No se pudo conectar con el servidor"
            );

        }

    };


    // ========================================================
    // CARGA INICIAL + ACTUALIZACIÓN AUTOMÁTICA
    // ========================================================

    useEffect(() => {

        loadMessages();

        const interval = setInterval(
            loadMessages,
            3000
        );

        return () => clearInterval(interval);

    }, []);


    // ========================================================
    // ENVIAR MENSAJE
    // ========================================================

    const sendMessage = async () => {

        const text = message.trim();

        if (text === "") {
            return;
        }


        if (sender === receiver) {

            alert(
                "El remitente y destinatario deben ser diferentes."
            );

            return;

        }


        try {

            const response = await fetch(
                `${API_URL}/messages`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({

                        sender: sender,

                        receiver: receiver,

                        message: text

                    })

                }
            );


            if (!response.ok) {

                const error =
                    await response.json();

                throw new Error(
                    error.detail ||
                    "Error al enviar el mensaje"
                );

            }


            // Limpiar input

            setMessage("");


            // Actualizar chat

            await loadMessages();


        } catch (error) {

            console.error(error);

            setStatus(
                "Error al enviar el mensaje"
            );

        }

    };


    // ========================================================
    // ENTER PARA ENVIAR
    // ========================================================

    const handleKeyDown = (event) => {

        if (event.key === "Enter") {

            event.preventDefault();

            sendMessage();

        }

    };


    // ========================================================
    // INTERFAZ
    // ========================================================

    return (

        <div className="app">

            <div className="chat-container">


                {/* ==========================================
                    HEADER
                ========================================== */}

                <header className="chat-header">

                    <div>

                        <h1>
                            Chat Seguro
                        </h1>

                        <p>
                            CIA Triad
                        </p>

                    </div>

                    <div className="connection">

                        <span className="online-dot"></span>

                        Seguro

                    </div>

                </header>


                {/* ==========================================
                    USUARIOS
                ========================================== */}

                <div className="user-controls">

                    <div className="user-select">

                        <label>
                            Soy
                        </label>

                        <select
                            value={sender}
                            onChange={(e) =>
                                setSender(e.target.value)
                            }
                        >

                            <option value="Usuario A">
                                👤 Usuario A
                            </option>

                            <option value="Usuario B">
                                👤 Usuario B
                            </option>

                        </select>

                    </div>


                    <div className="arrow">
                        →
                    </div>


                    <div className="user-select">

                        <label>
                            Enviar a
                        </label>

                        <select
                            value={receiver}
                            onChange={(e) =>
                                setReceiver(e.target.value)
                            }
                        >

                            <option value="Usuario B">
                                👤 Usuario B
                            </option>

                            <option value="Usuario A">
                                👤 Usuario A
                            </option>

                        </select>

                    </div>

                </div>


                {/* ==========================================
                    MENSAJES
                ========================================== */}

                <main className="messages">

                    {messages.length === 0 ? (

                        <div className="empty">

                            <div className="empty-icon">
                                
                            </div>

                            <h2>
                                No hay mensajes
                            </h2>

                            <p>
                                Envía el primer mensaje seguro.
                            </p>

                        </div>

                    ) : (

                        messages.map((msg) => (

                            <div
                                key={msg.id}
                                className={
                                    msg.sender === sender
                                        ? "message-wrapper own"
                                        : "message-wrapper"
                                }
                            >

                                <div className="message">

                                    <div className="message-header">

                                        <strong>
                                            {msg.sender}
                                        </strong>

                                        <span>
                                            {new Date(
                                                msg.timestamp
                                            ).toLocaleTimeString(
                                                "es-MX",
                                                {
                                                    hour: "2-digit",
                                                    minute: "2-digit"
                                                }
                                            )}
                                        </span>

                                    </div>


                                    <div className="message-text">

                                        {msg.message}

                                    </div>


                                    <div className="verification">

                                        {msg.verification ===
                                        "Mensaje verificado" ? (

                                            <span className="verified">
                                                ✓ Mensaje verificado
                                            </span>

                                        ) : (

                                            <span className="not-verified">
                                                No verificado
                                            </span>

                                        )}

                                    </div>

                                </div>

                            </div>

                        ))

                    )}

                </main>


                {/* ==========================================
                    INPUT
                ========================================== */}

                <div className="input-area">

                    <input
                        type="text"
                        placeholder="Escribe un mensaje seguro..."
                        value={message}
                        onChange={(e) =>
                            setMessage(e.target.value)
                        }
                        onKeyDown={handleKeyDown}
                    />

                    <button onClick={sendMessage}>

                        ➤

                    </button>

                </div>


                {/* ==========================================
                    STATUS
                ========================================== */}

                <div className="status">

                    {status}

                </div>


            </div>

        </div>

    );

}

export default App;