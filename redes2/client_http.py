import socket
import sys

# =============================
# CONFIGURAÇÕES
# =============================
SERVER_IP = "54.99.0.10"  # IP do container servidor
PORT = 8080

# Método HTTP recebido como argumento
# Exemplo: python3 client_http.py POST
if len(sys.argv) > 1:
    METHOD = sys.argv[1].upper()
else:
    METHOD = "GET"

# Corpo da requisição (para POST e PUT)
if METHOD in ["POST", "PUT"]:
    body = f"{{'mensagem': 'Teste de {METHOD} com sucesso!'}}"
else:
    body = ""

# Cabeçalhos da requisição
request = (
    f"{METHOD} / HTTP/1.1\r\n"
    f"Host: servidor_http\r\n"
    "User-Agent: DockerClient/1.0\r\n"
    "Accept: */*\r\n"
    "Connection: close\r\n"
)

if body:
    request += f"Content-Length: {len(body)}\r\n"
    request += "Content-Type: application/json\r\n"

request += "\r\n"  # fim dos cabeçalhos

if body:
    request += body

# =============================
# ENVIA A REQUISIÇÃO
# =============================
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((SERVER_IP, PORT))
    s.sendall(request.encode())

    response = s.recv(4096).decode()
    print(f"[CLIENTE] Requisição {METHOD} enviada para {SERVER_IP}:{PORT}")
    print("\n[RESPOSTA DO SERVIDOR]")
    print(response)
