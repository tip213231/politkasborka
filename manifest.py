import os
import hashlib
import json

# === НАСТРОЙКА ПУТЕЙ GITHUB ===
GITHUB_USER = "tip213231"              # Твой ник на GitHub
GITHUB_REPO = "politkasborka"  # Название твоего репозитория
BRANCH = "main"                          # Ветка для обычных файлов
RELEASE_TAG = "v1.0.0"                   # Тег релиза, куда ты загрузил .zip архивы

TARGET_DIR = "dist"
OUTPUT_FILE = "manifest.json"

# Базовые URL для формирования ссылок
RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{BRANCH}/"
RELEASE_URL = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/releases/download/{RELEASE_TAG}/"

def calculate_sha256(file_path):
    """Считает SHA-256 хэш файла блоками"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def generate_manifest():
    manifest = {
        "version": "1.0.0", # Меняй версию (например, 1.0.1) при каждом обновлении модов
        "minecraft_version": "1.20.1",
        "main_class": "net.minecraft.client.main.Main",
        "jvm_args": "-Xmx4G -XX:+UseG1GC",
        "files": []
    }

    # Обходим файлы в папке сборки
    for root, dirs, files in os.walk(TARGET_DIR):
        # Игнорируем распакованные папки assets и libraries на всякий случай,
        # чтобы они случайно не попали в манифест, если ты забыл их удалить.
        if "assets" in root.split(os.sep) or "libraries" in root.split(os.sep):
            continue

        for file in files:
            full_path = os.path.join(root, file)
            
            # Получаем относительный путь (например, "client/mods/sodium.jar" или "assets.zip")
            relative_path = os.path.relpath(full_path, TARGET_DIR).replace("\\", "/")
            
            file_hash = calculate_sha256(full_path)
            file_size = os.path.getsize(full_path)
            
            # РАСПРЕДЕЛЕНИЕ ССЫЛОК:
            # Если файл — это один из наших тяжелых архивов
            if relative_path in ["assets.zip", "libraries.zip"]:
                file_url = f"{RELEASE_URL}{relative_path}"
                action = "extract"  # Сигнал для Rust: после скачивания распаковать!
            else:
                # Все остальные файлы (моды, конфиги, джарник игры) тянутся из репозитория напрямую
                file_url = f"{RAW_URL}{relative_path}"
                action = "none"     # Сигнал для Rust: просто скачать и положить по пути

            print(f"Добавлен файл: {relative_path}")
            print(f"  └─ Ссылка: {file_url}")
            print(f"  └─ Действие: {action}\n")

            manifest["files"].append({
                "path": relative_path,
                "hash": file_hash,
                "size": file_size,
                "url": file_url,
                "action": action
            })

    # Сохраняем итоговый manifest.json
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        
    print(f" Успех! {OUTPUT_FILE} сгенерирован под новую структуру GitHub.")

if __name__ == "__main__":
    generate_manifest()