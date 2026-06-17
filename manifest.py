import os
import hashlib
import json

# Конфигурация
TARGET_DIR = "dist"  # Папка со сборкой
BASE_URL = "https://your-supabase-id.supabase.co/storage/v1/object/public/minecraft-dist/"
OUTPUT_FILE = "manifest.json"

def calculate_sha256(file_path):
    """Считает SHA-256 хэш файла блоками, чтобы не жрать оперативку"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def generate_manifest():
    manifest = {
        "version": "1.0.0",
        "minecraft_version": "1.21.1",
        "main_class": "net.minecraft.client.main.Main",
        "jvm_args": "-Xmx4G -XX:+UseG1GC",
        "files": []
    }

    # Обходим все файлы в папке сборки
    for root, dirs, files in os.walk(TARGET_DIR):
        for file in files:
            full_path = os.path.join(root, file)
            
            # Получаем относительный путь (например, "client/mods/sodium.jar")
            relative_path = os.path.relpath(full_path, TARGET_DIR).replace("\\", "/")
            
            print(f"Обработка: {relative_path}")
            
            file_hash = calculate_sha256(full_path)
            file_size = os.path.getsize(full_path)
            
            # Формируем прямую ссылку на скачивание из Supabase Storage
            file_url = f"{BASE_URL}{relative_path}"

            manifest["files"].append({
                "path": relative_path,
                "hash": file_hash,
                "size": file_size,
                "url": file_url
            })

    # Сохраняем в JSON с отступами для читаемости
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        
    print(f"\n Готово! Манифест успешно сохранен в {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_manifest()