#!/bin/bash

echo "=================================================="
echo "   PROJETO: SERVIDORES WEB - SEQUENCIAL vs CONCORRENTE"
echo "   Matrícula: 20219015426"
echo "   Aluno: Alisson Rodrigo"
echo "=================================================="
echo ""

mkdir -p results

echo " Limpando ambiente anterior..."
docker-compose down -v 2>/dev/null
echo ""

echo " Construindo imagens Docker..."
docker-compose build || { echo "❌ Erro ao construir as imagens!"; exit 1; }
echo ""

echo " Iniciando containers..."
docker-compose up -d || { echo "❌ Erro ao iniciar os containers!"; exit 1; }
echo ""

echo " Aguardando containers estabilizarem (10 segundos)..."
sleep 10
echo ""

echo "=================================================="
echo "   VERIFICANDO CONECTIVIDADE DA REDE"
echo "=================================================="
echo ""

docker exec cliente ping -c 3 54.99.0.10
docker exec cliente ping -c 3 54.99.0.11
echo ""

echo "=================================================="
echo "   INICIANDO TESTES DE DESEMPENHO"
echo "=================================================="
echo ""

docker exec cliente bash -lc "
echo ' Aguardando servidores iniciarem...'
sleep 5

if [ -f '/app/results/results.csv' ]; then
    rm /app/results/results.csv
    echo '  Arquivo de resultados anterior removido'
fi

echo ''
echo '=================================================='
echo '   TESTANDO SERVIDOR SEQUENCIAL (54.99.0.10)'
echo '=================================================='
python3 /app/metrics.py 54.99.0.10 sequencial 30

echo ''
echo '=================================================='
echo '   TESTANDO SERVIDOR CONCORRENTE (54.99.0.11)'
echo '=================================================='
python3 /app/metrics.py 54.99.0.11 concorrente 30

echo ''
echo '=================================================='
echo '   GERANDO GRÁFICOS'
echo '=================================================='
python3 /app/plot_results.py

echo ''
echo ' TESTES CONCLUÍDOS!'
echo ' Resultados salvos em: /app/results/results.csv'
echo ' Gráfico salvo em: /app/results/graph.png'
"

echo ""
echo " Copiando resultados do container para o host..."
mkdir -p ./results

docker cp cliente:/app/results.csv ./results/results.csv 2>/dev/null && \
    echo " Arquivo results.csv copiado com sucesso!" || \
    echo "  results.csv não encontrado no container."

docker cp cliente:/app/graph.png ./results/graph.png 2>/dev/null && \
    echo " Arquivo graph.png copiado com sucesso!" || \
    echo "  graph.png não encontrado no container."

echo ""
echo "=================================================="
echo "   RESULTADOS FINAIS"
echo "=================================================="
if [ -f "./results/results.csv" ]; then
    cat ./results/results.csv
else
    echo "  Arquivo results.csv não encontrado."
fi

if [ -f "./results/graph.png" ]; then
    echo " Gráfico disponível em ./results/graph.png"
fi

echo ""
echo "=================================================="
echo "   OPÇÕES"
echo "=================================================="
echo "Para ver logs:"
echo "  docker-compose logs servidor_sequencial"
echo "  docker-compose logs servidor_concorrente"
echo ""
echo "Para parar tudo:"
echo "  docker-compose down"
echo ""
echo " Execução finalizada com sucesso!"
