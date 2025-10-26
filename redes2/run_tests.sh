#!/bin/bash


echo "=================================================="
echo "   INICIANDO TESTES DE DESEMPENHO"
echo "=================================================="
echo ""

echo "⏳ Aguardando servidores iniciarem..."
sleep 5

if [ -f "/app/results/results.csv" ]; then
    rm /app/results/results.csv
    echo "🗑️  Arquivo de resultados anterior removido"
fi

echo ""
echo "=================================================="
echo "   TESTANDO SERVIDOR SEQUENCIAL (54.99.0.10)"
echo "=================================================="
python3 /app/metrics.py 54.99.0.10 sequencial 10

echo ""
echo "=================================================="
echo "   TESTANDO SERVIDOR CONCORRENTE (54.99.0.11)"
echo "=================================================="
python3 /app/metrics.py 54.99.0.11 concorrente 10

echo ""
echo "=================================================="
echo "   GERANDO GRÁFICOS"
echo "=================================================="
python3 /app/plot_results.py

echo ""
echo "TESTES CONCLUÍDOS!"
echo "Resultados salvos em: /app/results.csv"
echo "Gráfico salvo em: /app/graph.png"
echo ""