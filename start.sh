#!/bin/bash

echo "🟡 Iniciando aplicação Flask..."

# Ativa ambiente virtual, se existir
if [ -d "venv" ]; then
  source venv/bin/activate
  echo "✅ Ambiente virtual ativado."
fi

# Define variáveis de ambiente
export FLASK_APP=run.py
export FLASK_ENV=development

# Cria banco de dados se necessário
if [ ! -f "app/db.sqlite3" ]; then
  echo "📦 Criando banco de dados..."
  python3 run.py >/dev/null 2>&1 &
  sleep 3
  kill $!
  echo "✅ Banco de dados criado."
fi

# Inicia servidor Flask
echo "🚀 Rodando em http://0.0.0.0:5000/"
flask run --host=0.0.0.0 --port=5000
