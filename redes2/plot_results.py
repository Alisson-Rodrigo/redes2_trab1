import csv

import matplotlib.pyplot as plt
import numpy as np

file_path = "/app/results.csv"

tipos, metodos, medias, desvios, throughput = [], [], [], [], []

with open(file_path, newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        tipos.append(row["tipo_servidor"])
        metodos.append(row["metodo"])
        medias.append(float(row["media"]))
        desvios.append(float(row["desvio"]))
        throughput.append(float(row["throughput"]))

metodos_unicos = sorted(set(metodos))
servidores = sorted(set(tipos))
x = np.arange(len(metodos_unicos))
largura = 0.35

fig, ax = plt.subplots(1, 2, figsize=(10, 4))


for i, servidor in enumerate(servidores):
    valores = [medias[j] for j in range(len(medias)) if tipos[j] == servidor]
    ax[0].bar(x + i * largura, valores, largura, label=servidor, alpha=0.8)
ax[0].set_xticks(x + largura / 2)
ax[0].set_xticklabels(metodos_unicos)
ax[0].set_title("Tempo Médio por Método")
ax[0].set_ylabel("Tempo (s)")
ax[0].legend()
ax[0].grid(axis="y", linestyle="--", alpha=0.7)


for i, servidor in enumerate(servidores):
    valores = [throughput[j]
               for j in range(len(throughput)) if tipos[j] == servidor]
    ax[1].bar(x + i * largura, valores, largura, label=servidor, alpha=0.8)
ax[1].set_xticks(x + largura / 2)
ax[1].set_xticklabels(metodos_unicos)
ax[1].set_title("Throughput por Método")
ax[1].set_ylabel("Requisições por segundo")
ax[1].grid(axis="y", linestyle="--", alpha=0.7)

plt.suptitle("Desempenho: Servidor Sequencial vs Concorrente")
plt.tight_layout()
plt.savefig("/app/graph.png", dpi=150)
print("📊 Gráficos salvos em /app/graph.png")
