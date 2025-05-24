# Time Bot API

## Запуск:

1. Установите Ollama:
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2 latest
Запустите сервер:

bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
ollama serve &  # В отдельном терминале
python main.py
