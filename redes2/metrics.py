import csv
import hashlib
import socket
import statistics
import sys
import time
import threading
import subprocess

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

# Matrícula e Nome para gerar X-Custom-ID
MATRICULA = "20219015499"
NOME = "Alisson Rodrigo"


def gerar_custom_id(matricula, nome):
    """Gera o hash MD5 da matrícula e nome"""
    texto = f"{matricula} {nome}"
    return hashlib.md5(texto.encode()).hexdigest()


CUSTOM_ID = gerar_custom_id(MATRICULA, NOME)
print(f"[INFO] X-Custom-ID gerado: {CUSTOM_ID}\n")


# ==================================================
# FUNÇÃO DE REQUISIÇÃO (mantida para compatibilidade)
# ==================================================
def medir_tempo_resposta(method):
    """Envia requisição HTTP e mede o tempo de resposta"""
    corpo = ""
    if method in ["POST", "PUT"]:
        corpo = '{"mensagem":"teste"}'

    request = (
        f"{method} / HTTP/1.1\r\n"
        f"Host: {SERVER_IP}\r\n"
        "User-Agent: BenchClient/1.0\r\n"
        "Accept: */*\r\n"
        f"X-Custom-ID: {CUSTOM_ID}\r\n"
        "Connection: close\r\n"
    )
    
    if corpo:
        request += f"Content-Length: {len(corpo)}\r\n"
        request += "Content-Type: application/json\r\n"
    
    request += "\r\n"
    
    if corpo:
        request += corpo

    inicio = time.time()
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect((SERVER_IP, PORT))
            s.sendall(request.encode())
            
            response = s.recv(4096).decode()
            
            if "401" in response.split("\r\n")[0]:
                print(f"   ⚠️  ERRO: Autenticação falhou!")
                return None
                
    except Exception as e:
        print(f"   ❌ ERRO na conexão: {e}")
        return None
    
    fim = time.time()
    return fim - inicio


# ==================================================
# TESTES PARA SERVIDOR SEQUENCIAL
# ==================================================
def testar_servidor_sequencial():
    """Testa servidor sequencial com requisições uma por vez"""
    print(f"[TESTES] Servidor SEQUENCIAL ({SERVER_IP})")
    print(f"[TESTES] {NUM_TESTES} execuções por método\n")
    print("=" * 60)
    
    all_results = []
    
    for method in METODOS:
        tempos = []
        print(f"\n👉 Método {method}:")
        
        for i in range(NUM_TESTES):
            t = medir_tempo_resposta(method)
            
            if t is None:
                print(f"   ❌ Teste {i+1}: FALHOU")
                continue
                
            tempos.append(t)
            print(f"   ✓ Teste {i+1}: {t:.5f} segundos")
        
        if not tempos:
            print(f"   ⚠️  Nenhum teste bem-sucedido para {method}")
            continue
        
        # Calcula estatísticas
        media = statistics.mean(tempos)
        desvio = statistics.stdev(tempos) if len(tempos) > 1 else 0.0
        throughput = len(tempos) / sum(tempos)
        
        print(f"\n📊 Estatísticas {method}:")
        print(f"   • Média: {media:.5f}s")
        print(f"   • Desvio: {desvio:.5f}s")
        print(f"   • Throughput: {throughput:.2f} req/s")
        print(f"   • Testes válidos: {len(tempos)}/{NUM_TESTES}")
        
        all_results.append((TIPO_SERVIDOR, method, media, desvio, throughput))
    
    return all_results


# ==================================================
# TESTES PARA SERVIDOR CONCORRENTE
# ==================================================
def testar_servidor_concorrente():
    """Testa servidor concorrente com requisições simultâneas"""
    print(f"[TESTES] Servidor CONCORRENTE ({SERVER_IP})")
    print(f"[TESTES] Testando com carga concorrente\n")
    print("=" * 60)
    
    all_results = []
    NUM_THREADS_CONCURRENT = 10  # Número de requisições simultâneas
    
    for method in METODOS:
        print(f"\n👉 Método {method} (modo concorrente):")
        
        tempos_totais = []
        throughputs = []
        
        # Executa NUM_TESTES vezes o teste de concorrência
        for teste in range(NUM_TESTES):
            tempos = []
            lock = threading.Lock()
            
            def fazer_requisicao(thread_id):
                t = medir_tempo_resposta(method)
                if t is not None:
                    with lock:
                        tempos.append(t)
            
            # Cria threads
            threads = []
            for i in range(NUM_THREADS_CONCURRENT):
                t = threading.Thread(target=fazer_requisicao, args=(i+1,))
                threads.append(t)
            
            # Inicia todas ao mesmo tempo
            inicio_total = time.time()
            for t in threads:
                t.start()
            
            # Aguarda todas finalizarem
            for t in threads:
                t.join()
            
            fim_total = time.time()
            tempo_total = fim_total - inicio_total
            
            if tempos:
                throughput = len(tempos) / tempo_total
                tempos_totais.append(tempo_total)
                throughputs.append(throughput)
                print(f"   ✓ Teste {teste+1}: {len(tempos)}/{NUM_THREADS_CONCURRENT} req em {tempo_total:.5f}s | Throughput: {throughput:.2f} req/s")
            else:
                print(f"   ❌ Teste {teste+1}: FALHOU")
        
        if not tempos_totais:
            print(f"   ⚠️  Nenhum teste bem-sucedido para {method}")
            continue
        
        # Calcula estatísticas gerais
        media_tempo = statistics.mean(tempos_totais)
        desvio_tempo = statistics.stdev(tempos_totais) if len(tempos_totais) > 1 else 0.0
        throughput_medio = statistics.mean(throughputs)
        
        print(f"\n📊 Estatísticas {method} (concorrente):")
        print(f"   • Tempo médio total: {media_tempo:.5f}s")
        print(f"   • Desvio padrão: {desvio_tempo:.5f}s")
        print(f"   • Throughput médio: {throughput_medio:.2f} req/s")
        print(f"   • Testes válidos: {len(tempos_totais)}/{NUM_TESTES}")
        
        # Salva resultado (usa tempo médio por requisição)
        tempo_medio_por_req = media_tempo / NUM_THREADS_CONCURRENT
        all_results.append((TIPO_SERVIDOR, method, tempo_medio_por_req, desvio_tempo, throughput_medio))
    
    return all_results


# ==================================================
# EXECUÇÃO PRINCIPAL
# ==================================================
if TIPO_SERVIDOR == "sequencial":
    all_results = testar_servidor_sequencial()
elif TIPO_SERVIDOR == "concorrente":
    all_results = testar_servidor_concorrente()
else:
    print(f"❌ Tipo de servidor inválido: {TIPO_SERVIDOR}")
    print("Use 'sequencial' ou 'concorrente'")
    sys.exit(1)


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

print("\n" + "=" * 60)
print(f"✅ Resultados salvos em {RESULTS_FILE}")
print("=" * 60)