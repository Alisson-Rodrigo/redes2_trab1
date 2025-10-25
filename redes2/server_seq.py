import hashlib
import socket

# ============================================
# CONFIGURAÇÕES
# ============================================
HOST = "0.0.0.0"
PORT = 8080

# Matrícula e nome para o hash
MATRICULA = "20219015499"
NOME = "Alisson Rodrigo"


def gerar_custom_id(matricula, nome):
    texto = f"{matricula} {nome}"
    return hashlib.md5(texto.encode()).hexdigest()


CUSTOM_ID = gerar_custom_id(MATRICULA, NOME)
print(f"[INFO] X-Custom-ID gerado: {CUSTOM_ID}")

# ============================================
# INICIALIZA O SERVIDOR SEQUENCIAL
# ============================================
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(1)

    print(f"[SERVIDOR] Servidor SEQUENCIAL escutando em {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        with conn:
            print(f"[SERVIDOR] Conexão recebida de {addr}")

            data = conn.recv(4096).decode()
            if not data:
                continue

            print(f"[REQUISIÇÃO RECEBIDA DE {addr}]\n{data}")

            # Identifica o método HTTP
            metodo = data.split(" ")[0].upper()

            # Resposta para requisição OPTIONS (pré-flight CORS)
            if metodo == "OPTIONS":
                resposta = (
                    "HTTP/1.1 204 No Content\r\n"
                    "Access-Control-Allow-Origin: *\r\n"
                    "Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS\r\n"
                    "Access-Control-Allow-Headers: Content-Type, X-Custom-ID\r\n"
                    "Connection: close\r\n\r\n"
                )
                conn.sendall(resposta.encode())
                continue

            # Corpo da resposta
            if metodo == "GET":
                corpo = f"Requisição GET recebida de {addr}\n"
            elif metodo == "POST":
                corpo = f"Requisição POST recebida de {addr}\n"
            elif metodo == "PUT":
                corpo = f"Requisição PUT recebida de {addr}\n"
            elif metodo == "DELETE":
                corpo = f"Requisição DELETE recebida de {addr}\n"
            else:
                corpo = f"Método {metodo} não suportado.\n"

            # Monta resposta HTTP com cabeçalhos CORS
            resposta = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/plain; charset=utf-8\r\n"
                "Access-Control-Allow-Origin: *\r\n"
                "Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS\r\n"
                "Access-Control-Allow-Headers: Content-Type, X-Custom-ID\r\n"
                f"X-Custom-ID: {CUSTOM_ID}\r\n"
                "Connection: close\r\n"
                "\r\n"
                f"{corpo}"
            )

            conn.sendall(resposta.encode())
            print(f"[SERVIDOR] Resposta enviada ({metodo}) para {addr}")
