#!/usr/bin/env python3
"""
Демонстрационный скрипт для проверки работы с Alpine Linux пакетами
"""

import json
import tempfile
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from visualizer import DependencyVisualizer


def demo_popular_packages():
    """Демонстрация для популярных пакетов Alpine"""
    packages = [
        "nginx",
        "busybox",
        "bash",
        "python3",
        "nodejs",
        "postgresql",
        "redis"
    ]

    config_template = {
        "repository_url": "https://dl-cdn.alpinelinux.org/alpine/v3.18/main",
        "test_repository_mode": False,
        "output_filename": "dependencies.png",
        "ascii_tree_output": False
    }

    for package in packages:
        print(f"\n{'=' * 60}")
        print(f"АНАЛИЗ ПАКЕТА: {package}")
        print(f"{'=' * 60}")

        config = config_template.copy()
        config["package_name"] = package

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            temp_path = f.name

        try:
            visualizer = DependencyVisualizer(temp_path)
            success = visualizer.run()

            if not success:
                print(f"⚠ Не удалось проанализировать пакет {package}")

        except Exception as e:
            print(f"❌ Ошибка при анализе пакета {package}: {e}")
        finally:
            os.unlink(temp_path)


def demo_with_test_data():
    """Демонстрация с тестовыми данными"""
    print(f"\n{'=' * 60}")
    print("ДЕМОНСТРАЦИЯ С ТЕСТОВЫМИ ДАННЫМИ")
    print(f"{'=' * 60}")

    # Создаем тестовый репозиторий
    test_repo_dir = tempfile.mkdtemp()
    index_content = """C:Q1W7Dd8KAmO3cXv4n6m9pLs2jRfBhTgY
P:web-server
V:1.0.0-r0
D:nginx openssl libc
i:web-server

C:R1a2B3c4D5e6F7g8H9i0Jk1Lm2N3o4P5
P:nginx
V:1.24.0-r10
D:musl libcrypto3 libssl3 pcre2 zlib
i:nginx

C:S2b3C4d5E6f7G8h9I0jK1lM2nO3p4Q5r
P:openssl
V:3.0.0-r0
D:musl libc
i:openssl

C:T3c4D5e6F7g8H9i0Jk1Lm2N3o4P5q6R7s
P:musl
V:1.2.4-r0
D:
i:musl

C:U4d5E6f7G8h9I0jK1lM2nO3p4Q5r6S7t8
P:libc
V:1.0.0-r0
D:
i:libc
"""

    index_path = os.path.join(test_repo_dir, "APKINDEX")
    with open(index_path, 'w') as f:
        f.write(index_content)

    config = {
        "package_name": "web-server",
        "repository_url": "https://example.com",
        "test_repository_mode": True,
        "test_repository_path": test_repo_dir,
        "output_filename": "web_server_dependencies.png",
        "ascii_tree_output": True
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config, f)
        temp_path = f.name

    try:
        visualizer = DependencyVisualizer(temp_path)
        visualizer.run()
    finally:
        import shutil
        shutil.rmtree(test_repo_dir)
        os.unlink(temp_path)


if __name__ == "__main__":
    print("ДЕМОНСТРАЦИЯ СИСТЕМЫ АНАЛИЗА ЗАВИСИМОСТЕЙ ALPINE LINUX")

    # Демонстрация с тестовыми данными
    demo_with_test_data()

    # Демонстрация с реальными данными (закомментировано, чтобы не грузить сеть)
    # print("\n" + "="*60)
    # print("ПРЕДУПРЕЖДЕНИЕ: Следующая демонстрация загружает данные из интернета")
    # print("и может занять некоторое время...")
    # print("="*60)
    # input("Нажмите Enter для продолжения...")
    # demo_popular_packages()