import hashlib
import socket

# ============================================
# CONFIGURAÇÕES
# ============================================
HOST = "0.0.0.0"
PORT = 80  
# Matrícula e nome para o hash
MATRICULA = "20219015499"
NOME = "Alisson Rodrigo"


def gerar_custom_id(matricula, nome):
    """Gera o hash MD5 da matrícula e nome"""
    texto = f"{matricula} {nome}"
    return hashlib.md5(texto.encode()).hexdigest()


def extrair_headers(data):
    """Extrai os cabeçalhos HTTP da requisição"""
    headers = {}
    lines = data.split('\r\n')
    
    # Pula a primeira linha (request line)
    for line in lines[1:]:
        if not line or line == '\r\n':
            break
        if ':' in line:
            key, value = line.split(':', 1)
            headers[key.strip().lower()] = value.strip()
    
    return headers


def validar_custom_id(headers, expected_id):
    """Valida se o X-Custom-ID está presente e correto"""
    client_id = headers.get('x-custom-id', '')
    
    if not client_id:
        return False, "X-Custom-ID ausente"
    
    if client_id != expected_id:
        return False, f"X-Custom-ID inválido"
    
    return True, "X-Custom-ID válido"


CUSTOM_ID = gerar_custom_id(MATRICULA, NOME)
print(f"[INFO] X-Custom-ID esperado: {CUSTOM_ID}")

# ============================================
# INICIALIZA O SERVIDOR SEQUENCIAL
# ============================================
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(1)

    print(f"[SERVIDOR] Servidor SEQUENCIAL escutando em {HOST}:{PORT}")
    print(f"[SERVIDOR] Pronto para aceitar conexões...\n")

    while True:
        conn, addr = server.accept()
        with conn:
            print(f"\n[SERVIDOR] Conexão recebida de {addr}")

            data = conn.recv(4096).decode()
            if not data:
                continue

            print(f"[REQUISIÇÃO RECEBIDA DE {addr}]")

            # Identifica o método HTTP
            metodo = data.split(" ")[0].upper() if data else "UNKNOWN"

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
                print(f"[SERVIDOR] Resposta OPTIONS enviada para {addr}")
                continue

            # ✅ VALIDAÇÃO DO X-Custom-ID
            headers = extrair_headers(data)
            valido, mensagem = validar_custom_id(headers, CUSTOM_ID)
            
            print(f"[VALIDAÇÃO] {mensagem}")
            
            if not valido:
                # Resposta 401 Unauthorized se X-Custom-ID inválido
                corpo = f"Erro de autenticação: {mensagem}\n"
                resposta = (
                    "HTTP/1.1 401 Unauthorized\r\n"
                    "Content-Type: text/plain; charset=utf-8\r\n"
                    "Access-Control-Allow-Origin: *\r\n"
                    f"X-Custom-ID: {CUSTOM_ID}\r\n"
                    "Connection: close\r\n"
                    f"Content-Length: {len(corpo.encode('utf-8'))}\r\n"
                    "\r\n"
                    f"{corpo}"
                )
                conn.sendall(resposta.encode())
                print(f"[SERVIDOR] Resposta 401 enviada para {addr} - {mensagem}")
                continue

            # Corpo da resposta para requisições válidas
            if metodo == "GET":
                corpo = f"Requisição GET recebida de {addr}\nX-Custom-ID validado com sucesso!\n"
            elif metodo == "POST":
                corpo = f"Requisição POST recebida de {addr}\nX-Custom-ID validado com sucesso!\n"
            elif metodo == "PUT":
                corpo = f"Requisição PUT recebida de {addr}\nX-Custom-ID validado com sucesso!\n"
            elif metodo == "DELETE":
                corpo = f"Requisição DELETE recebida de {addr}\nX-Custom-ID validado com sucesso!\n"
            else:
                corpo = f"Método {metodo} não suportado.\n"

            # Monta resposta HTTP 200 OK com cabeçalhos CORS
            resposta = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/plain; charset=utf-8\r\n"
                "Access-Control-Allow-Origin: *\r\n"
                "Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS\r\n"
                "Access-Control-Allow-Headers: Content-Type, X-Custom-ID\r\n"
                f"X-Custom-ID: {CUSTOM_ID}\r\n"
                "Connection: close\r\n"
                f"Content-Length: {len(corpo.encode('utf-8'))}\r\n"
                "\r\n"
                f"{corpo}"
            )

            conn.sendall(resposta.encode())
            print(f"[SERVIDOR] Resposta 200 OK enviada para {addr} - Método: {metodo}")