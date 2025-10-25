import csv
import socket
import statistics
import sys
import time

# ==================================================
# CONFIGURAÇÕES
# ==================================================
if len(sys.argv) < 3:
    print("Uso: python3 metrics.py <SERVER_IP> <TIPO_SERVIDOR> [NUM_TESTES]")
    sys.exit(1)

SERVER_IP = sys.argv[1]  # ex: 54.99.0.10
PORT = 8080
TIPO_SERVIDOR = sys.argv[2]  # "sequencial" ou "concorrente"
NUM_TESTES = int(sys.argv[3]) if len(sys.argv) > 3 else 10
RESULTS_FILE = "/app/results.csv"

METODOS = ["GET", "POST", "PUT", "DELETE"]

# ==================================================
# FUNÇÃO DE REQUISIÇÃO
# ==================================================


def medir_tempo_resposta(method):
    corpo = ""
    if method in ["POST", "PUT"]:
        corpo = '{"mensagem":"teste"}'

    request = (
        f"{method} / HTTP/1.1\r\n"
        f"Host: {SERVER_IP}\r\n"
        "User-Agent: BenchClient/1.0\r\n"
        "Accept: */*\r\n"
        "Connection: close\r\n"
        + (f"Content-Length: {len(corpo)}\r\n\r\n{corpo}" if corpo else "\r\n")
    )

    inicio = time.time()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER_IP, PORT))
        s.sendall(request.encode())
        try:
            s.recv(4096)
        except Exception:
            pass
    fim = time.time()
    return fim - inicio


# ==================================================
# EXECUÇÃO DOS TESTES
# ==================================================
print(
    f"\n[TESTES] Servidor {TIPO_SERVIDOR.upper()} ({SERVER_IP}) - {NUM_TESTES} execuções por método")

all_results = []

for method in METODOS:
    tempos = []
    print(f"\n👉 Método {method}:")
    for i in range(NUM_TESTES):
        t = medir_tempo_resposta(method)
        tempos.append(t)
        print(f" - Teste {i+1}: {t:.5f} segundos")
    media = statistics.mean(tempos)
    desvio = statistics.stdev(tempos) if len(tempos) > 1 else 0.0
    throughput = NUM_TESTES / sum(tempos)
    print(
        f"📊 Média: {media:.5f}s | Desvio: {desvio:.5f}s | Throughput: {throughput:.2f} req/s")
    all_results.append((TIPO_SERVIDOR, method, media, desvio, throughput))

# ==================================================
# SALVA RESULTADOS NO CSV
# ==================================================
header = ["tipo_servidor", "metodo", "media", "desvio", "throughput"]

try:
    with open(RESULTS_FILE, "x", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
except FileExistsError:
    pass

with open(RESULTS_FILE, "a", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(all_results)

print(f"\n✅ Resultados salvos em {RESULTS_FILE}")
