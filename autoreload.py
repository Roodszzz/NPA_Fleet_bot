import subprocess
import sys
import time
import os

# Путь к вашему Python в venv
PYTHON = r"C:\Users\OleRud441\OneDrive - Norwegian People's Aid\Desktop\NPA_Fleet_bot\venv\Scripts\python.exe"
# Путь к вашему боту
BOT = r"C:\Users\OleRud441\OneDrive - Norwegian People's Aid\Desktop\NPA_Fleet_bot\bot.py"

def run_bot():
    """Запускаем бота и перезапускаем при изменении кода."""
    process = subprocess.Popen([PYTHON, BOT])
    return process

def watch():
    """Отслеживаем изменения .py файлов и перезапускаем бот."""
    files_mtime = {}
    for root, _, files in os.walk(os.path.dirname(BOT)):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                files_mtime[path] = os.path.getmtime(path)

    process = run_bot()

    try:
        while True:
            time.sleep(1)
            changed = False
            for path, last_mtime in files_mtime.items():
                if os.path.exists(path):
                    current_mtime = os.path.getmtime(path)
                    if current_mtime != last_mtime:
                        files_mtime[path] = current_mtime
                        changed = True
            if changed:
                print("🔄 Перезапуск бота из-за изменений в коде...")
                process.terminate()
                process.wait()
                process = run_bot()
    except KeyboardInterrupt:
        process.terminate()
        process.wait()
        print("❌ Перезапуск остановлен вручную.")

if __name__ == "__main__":
    watch()
