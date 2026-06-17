import os
import hashlib
import json

# === НАСТРОЙКА ПУТЕЙ GITHUB ===
GITHUB_USER = "tip213231"                # Твой ник на GitHub
GITHUB_REPO = "politkasborka"            # Название твоего репозитория
RELEASE_TAG = "v1.0.0"                   # Тег релиза для .zip архивов

# Базовые URL для формирования ссылок
PAGES_URL = f"https://{GITHUB_USER}.github.io/{GITHUB_REPO}/dist/"
RELEASE_URL = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/releases/download/{RELEASE_TAG}/"

# Указываем на подпапку dist, как у тебя на скриншотах
TARGET_DIR = "dist"
OUTPUT_FILE = "manifest.json"

def calculate_sha256(file_path):
    """Считает SHA-256 хэш файла блоками"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def generate_manifest():
    if not os.path.exists(TARGET_DIR):
        print(f"❌ Ошибка: Папка '{TARGET_DIR}' не найдена! Проверь, где запущен скрипт.")
        return

    manifest = {
        "version": "1.0.0", 
        "minecraft_version": "1.21.1",
        "main_class": "net.minecraft.client.main.Main",
        "jvm_args": "-Xmx4G -XX:+UseG1GC",
        "files": []
    }

    files_counter = 0

    # Обходим файлы внутри папки dist
    for root, dirs, files in os.walk(TARGET_DIR):
        # На всякий случай игнорируем распакованные папки, если они появятся
        if "assets" in root.split(os.sep) or "libraries" in root.split(os.sep):
            continue

        for file in files:
            full_path = os.path.join(root, file)
            
            # Получаем относительный путь БЕЗ папки dist/ в начале 
            # (например, "client/mods/sodium.jar" или "assets.zip")
            relative_path = os.path.relpath(full_path, TARGET_DIR).replace("\\", "/")
            
            file_hash = calculate_sha256(full_path)
            file_size = os.path.getsize(full_path)
            
            # Распределяем ссылки
            if relative_path in ["assets.zip", "libraries.zip"]:
                file_url = f"{RELEASE_URL}{relative_path}"
                action = "extract"
            else:
                file_url = f"{PAGES_URL}{relative_path}"
                action = "none"

            print(f"Добавлен [#{files_counter + 1}]: {relative_path}")
            print(f"  └─ URL: {file_url}")

            manifest["files"].append({
                "path": relative_path,
                "hash": file_hash,
                "size": file_size,
                "url": file_url,
                "action": action
            })
            files_counter += 1

    # Сохраняем manifest.json в корень politkasborka
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        
    print(f"\n Найдено и обработано файлов: {files_counter}")
    print(f" Успех! Манифест сохранен в: {os.path.abspath(OUTPUT_FILE)}")

if __name__ == "__main__":
    generate_manifest()