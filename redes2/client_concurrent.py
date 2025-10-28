import socket
import sys
import hashlib
import threading
import time

SERVER_IP = "54.99.0.10"  
PORT = 80 
MATRICULA = "20219015426"
NOME = "Alisson Rodrigo"

NUM_THREADS = int(sys.argv[1]) if len(sys.argv) > 1 else 5
METHOD = sys.argv[2].upper() if len(sys.argv) > 2 else "GET"


def gerar_custom_id(matricula, nome):
    """Gera o hash MD5 da matrícula e nome"""
    texto = f"{matricula} {nome}"
    return hashlib.md5(texto.encode()).hexdigest()


CUSTOM_ID = gerar_custom_id(MATRICULA, NOME)

resultados = []
resultado_lock = threading.Lock()


def enviar_requisicao(thread_id):
    """Envia uma requisição HTTP ao servidor"""
    try:
        if METHOD in ["POST", "PUT"]:
            body = f'{{"mensagem": "Thread {thread_id} - Teste {METHOD}"}}'
        else:
            body = ""

        request = (
            f"{METHOD} / HTTP/1.1\r\n"
            f"Host: servidor_http\r\n"
            f"User-Agent: ConcurrentClient/1.0 Thread-{thread_id}\r\n"
            "Accept: */*\r\n"
            f"X-Custom-ID: {CUSTOM_ID}\r\n"
            "Connection: close\r\n"
        )

        if body:
            request += f"Content-Length: {len(body)}\r\n"
            request += "Content-Type: application/json\r\n"

        request += "\r\n"
        
        if body:
            request += body

        inicio = time.time()
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect((SERVER_IP, PORT))
            s.sendall(request.encode())
            
            response = s.recv(4096).decode()
            
        fim = time.time()
        tempo = fim - inicio
        
        status_line = response.split('\r\n')[0]
        status = "✓ OK" if "200" in status_line else "✗ ERRO"
        
        print(f"[Thread-{thread_id:02d}] {status} | Tempo: {tempo:.4f}s | Status: {status_line}")
        
        with resultado_lock:
            resultados.append({
                'thread_id': thread_id,
                'tempo': tempo,
                'sucesso': "200" in status_line
            })
            
    except Exception as e:
        print(f"[Thread-{thread_id:02d}] ✗ ERRO: {e}")
        with resultado_lock:
            resultados.append({
                'thread_id': thread_id,
                'tempo': None,
                'sucesso': False
            })

print("=" * 70)
print(f"  TESTE DE CONCORRÊNCIA - Servidor {SERVER_IP}:{PORT}")
print("=" * 70)
print(f"  X-Custom-ID: {CUSTOM_ID}")
print(f"  Método: {METHOD}")
print(f"  Threads simultâneas: {NUM_THREADS}")
print("=" * 70)
print()

inicio_total = time.time()

threads = []
for i in range(NUM_THREADS):
    t = threading.Thread(target=enviar_requisicao, args=(i+1,))
    threads.append(t)

print(f"🚀 Enviando {NUM_THREADS} requisições simultâneas...\n")

for t in threads:
    t.start()

for t in threads:
    t.join()

fim_total = time.time()
tempo_total = fim_total - inicio_total


print()
print("=" * 70)
print("  ESTATÍSTICAS")
print("=" * 70)

sucessos = sum(1 for r in resultados if r['sucesso'])
falhas = len(resultados) - sucessos

tempos_validos = [r['tempo'] for r in resultados if r['tempo'] is not None]

if tempos_validos:
    tempo_medio = sum(tempos_validos) / len(tempos_validos)
    tempo_min = min(tempos_validos)
    tempo_max = max(tempos_validos)
    throughput = NUM_THREADS / tempo_total
    
    print(f"  Total de requisições: {NUM_THREADS}")
    print(f"  Sucessos: {sucessos} ({sucessos/NUM_THREADS*100:.1f}%)")
    print(f"  Falhas: {falhas} ({falhas/NUM_THREADS*100:.1f}%)")
    print(f"  Tempo total: {tempo_total:.4f}s")
    print(f"  Tempo médio por requisição: {tempo_medio:.4f}s")
    print(f"  Tempo mínimo: {tempo_min:.4f}s")
    print(f"  Tempo máximo: {tempo_max:.4f}s")
    print(f"  Throughput: {throughput:.2f} req/s")
else:
    print("  ⚠️  Nenhuma requisição bem-sucedida")

print("=" * 70)