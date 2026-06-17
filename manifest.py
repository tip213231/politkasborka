import os
import hashlib
import json

# === НАСТРОЙКА ПУТЕЙ GITHUB ===
GITHUB_USER = "tip213231"                # Твой новый ник на GitHub из ссылки
GITHUB_REPO = "politkasborka"            # Название твоего репозитория
RELEASE_TAG = "v1.0.0"                   # Тег релиза, куда загружены .zip архивы

# Новый базовый URL для GitHub Pages (все файлы кроме тяжелых архивов)
PAGES_URL = f"https://{GITHUB_USER}.github.io/{GITHUB_REPO}/dist/"

# URL для GitHub Releases (только для assets.zip и libraries.zip)
RELEASE_URL = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/releases/download/{RELEASE_TAG}/"

TARGET_DIR = "my_server_dist"
OUTPUT_FILE = "manifest.json"

def calculate_sha256(file_path):
    """Считает SHA-256 хэш файла блоками"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def generate_manifest():
    manifest = {
        "version": "1.0.0", # Не забывай повышать версию при обновлении модов!
        "minecraft_version": "1.20.1",
        "main_class": "net.minecraft.client.main.Main",
        "jvm_args": "-Xmx4G -XX:+UseG1GC",
        "files": []
    }

    # Обходим файлы в папке сборки
    for root, dirs, files in os.walk(TARGET_DIR):
        # Игнорируем распакованные папки ассетов и библиотек, если они случайно остались
        if "assets" in root.split(os.sep) or "libraries" in root.split(os.sep):
            continue

        for file in files:
            full_path = os.path.join(root, file)
            
            # Получаем относительный путь (например, "client/mods/sodium.jar" или "assets.zip")
            relative_path = os.path.relpath(full_path, TARGET_DIR).replace("\\", "/")
            
            file_hash = calculate_sha256(full_path)
            file_size = os.path.getsize(full_path)
            
            # РАСПРЕДЕЛЕНИЕ ССЫЛОК:
            if relative_path in ["assets.zip", "libraries.zip"]:
                # Тяжелые архивы по-прежнему тянем из Релизов
                file_url = f"{RELEASE_URL}{relative_path}"
                action = "extract"
            else:
                # ВСЕ остальное скачивается через быстрый GitHub Pages!
                file_url = f"{PAGES_URL}{relative_path}"
                action = "none"

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
        
    print(f" Успех! {OUTPUT_FILE} сгенерирован под GitHub Pages.")

if __name__ == "__main__":
    generate_manifest()