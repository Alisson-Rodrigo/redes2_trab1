import hashlib
import socket
import threading

HOST = "0.0.0.0"
PORT = 80 
MATRICULA = "20219015499"
NOME = "Alisson Rodrigo"


def gerar_custom_id(matricula, nome):
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


def handle_client(conn, addr):
    print(f"\n[CONEXÃO] Nova conexão de {addr} (Thread: {threading.current_thread().name})")
    
    try:
        data = conn.recv(4096).decode()
        if not data:
            return

        print(f"[REQUISIÇÃO DE {addr}]")

        # Identifica o método HTTP
        metodo = data.split(" ")[0].upper() if data else "UNKNOWN"

        # Resposta para pré-flight (CORS)
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
            return

        # ✅ VALIDAÇÃO DO X-Custom-ID
        headers = extrair_headers(data)
        valido, mensagem = validar_custom_id(headers, CUSTOM_ID)
        
        print(f"[VALIDAÇÃO {addr}] {mensagem}")
        
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
            return

        # Corpo da resposta para requisições válidas
        thread_info = f"Thread: {threading.current_thread().name}"
        if metodo == "GET":
            corpo = f"Requisição GET recebida de {addr}\nX-Custom-ID validado com sucesso!\n{thread_info}\n"
        elif metodo == "POST":
            corpo = f"Requisição POST recebida de {addr}\nX-Custom-ID validado com sucesso!\n{thread_info}\n"
        elif metodo == "PUT":
            corpo = f"Requisição PUT recebida de {addr}\nX-Custom-ID validado com sucesso!\n{thread_info}\n"
        elif metodo == "DELETE":
            corpo = f"Requisição DELETE recebida de {addr}\nX-Custom-ID validado com sucesso!\n{thread_info}\n"
        else:
            corpo = f"Método {metodo} não suportado.\n{thread_info}\n"

        # Resposta HTTP 200 OK com cabeçalhos CORS
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
        
    except Exception as e:
        print(f"[ERRO] Exceção ao processar {addr}: {e}")
    finally:
        conn.close()
        print(f"[SERVIDOR] Conexão com {addr} encerrada")


# =========================
# SERVIDOR PRINCIPAL
# =========================
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"[SERVIDOR] Concorrente escutando em {HOST}:{PORT}")
    print(f"[SERVIDOR] Pronto para aceitar conexões...\n")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        thread.start()
        active = threading.active_count() - 1  # Subtrai thread principal
        print(f"[SERVIDOR] Threads ativas: {active}")