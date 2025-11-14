#!/usr/bin/env python3
"""
Минимальный прототип визуализатора графа зависимостей пакетов
Этап 1: Конфигурация и базовое CLI
"""

import json
import os
import sys
from typing import Dict, Any, Optional
from pathlib import Path
import argparse


class ConfigError(Exception):
    """Класс для ошибок конфигурации"""
    pass


class DependencyVisualizer:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.required_params = [
            "package_name",
            "repository_url",
            "test_repository_mode",
            "output_filename"
        ]

    def load_config(self) -> None:
        """Загрузка конфигурации из JSON файла"""
        try:
            if not os.path.exists(self.config_path):
                raise ConfigError(f"Конфигурационный файл не найден: {self.config_path}")

            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)

        except json.JSONDecodeError as e:
            raise ConfigError(f"Ошибка парсинга JSON: {e}")
        except Exception as e:
            raise ConfigError(f"Ошибка загрузки конфигурации: {e}")

    def validate_config(self) -> None:
        """Валидация параметров конфигурации"""
        # Проверка обязательных параметров
        for param in self.required_params:
            if param not in self.config:
                raise ConfigError(f"Отсутствует обязательный параметр: {param}")

        # Проверка package_name
        package_name = self.config["package_name"]
        if not isinstance(package_name, str) or not package_name.strip():
            raise ConfigError("Имя пакета должно быть непустой строкой")

        # Проверка repository_url или test_repository_path
        if self.config.get("test_repository_mode", False):
            repo_path = self.config.get("test_repository_path", "")
            if not repo_path or not isinstance(repo_path, str):
                raise ConfigError("В режиме тестового репозитория должен быть указан test_repository_path")
            if not os.path.exists(repo_path):
                raise ConfigError(f"Тестовый репозиторий не найден: {repo_path}")
        else:
            repo_url = self.config["repository_url"]
            if not isinstance(repo_url, str) or not repo_url.strip():
                raise ConfigError("URL репозитория должен быть непустой строкой")
            if not (repo_url.startswith('http://') or repo_url.startswith('https://')):
                raise ConfigError("URL репозитория должен начинаться с http:// или https://")

        # Проверка output_filename
        output_file = self.config["output_filename"]
        if not isinstance(output_file, str) or not output_file.strip():
            raise ConfigError("Имя выходного файла должно быть непустой строкой")

        # Проверка ascii_tree_output
        ascii_tree = self.config.get("ascii_tree_output", False)
        if not isinstance(ascii_tree, bool):
            raise ConfigError("ascii_tree_output должен быть булевым значением")

    def display_config(self) -> None:
        """Вывод всех параметров конфигурации в формате ключ-значение"""
        print("=" * 50)
        print("ПАРАМЕТРЫ КОНФИГУРАЦИИ")
        print("=" * 50)

        for key, value in self.config.items():
            print(f"{key:25} : {value}")

        print("=" * 50)

    def generate_sample_dependencies(self) -> Dict[str, list]:
        """
        Генерация тестовых зависимостей для демонстрации
        В реальной реализации здесь будет логика получения зависимостей
        """
        sample_deps = {
            "example-package": ["requests", "numpy", "pandas"],
            "requests": ["urllib3", "chardet", "certifi"],
            "numpy": [],
            "pandas": ["numpy", "python-dateutil"],
            "urllib3": [],
            "chardet": [],
            "certifi": [],
            "python-dateutil": ["six"],
            "six": [],
            "test-package": ["example-package"]
        }
        return sample_deps

    def generate_ascii_tree(self, dependencies: Dict[str, list], package: str, prefix: str = "") -> str:
        """Генерация ASCII-дерева зависимостей"""
        if package not in dependencies:
            return f"{package} (не найден)\n"

        deps = dependencies[package]
        tree = f"{package}\n"

        for i, dep in enumerate(deps):
            is_last = i == len(deps) - 1
            tree += prefix + ("└── " if is_last else "├── ")
            tree += self.generate_ascii_tree(dependencies, dep, prefix + ("    " if is_last else "│   "))

        return tree

    def initialize(self) -> bool:
        """Инициализация приложения (загрузка и валидация конфигурации)"""
        try:
            # Загрузка и валидация конфигурации
            self.load_config()
            self.validate_config()
            return True
        except ConfigError as e:
            print(f"ОШИБКА КОНФИГУРАЦИИ: {e}", file=sys.stderr)
            return False
        except Exception as e:
            print(f"НЕИЗВЕСТНАЯ ОШИБКА: {e}", file=sys.stderr)
            return False

    def run(self) -> bool:
        """Основной метод запуска приложения"""
        # Загрузка и валидация конфигурации
        if not self.initialize():
            return False

        try:
            # Вывод параметров конфигурации
            self.display_config()

            # Демонстрация работы с зависимостями
            dependencies = self.generate_sample_dependencies()
            target_package = self.config["package_name"]

            print(f"\nАНАЛИЗ ПАКЕТА: {target_package}")
            print("=" * 30)

            if target_package in dependencies:
                print(f"Найдены зависимости для пакета '{target_package}':")

                # Вывод ASCII-дерева если включен режим
                if self.config.get("ascii_tree_output", False):
                    print("\nДЕРЕВО ЗАВИСИМОСТЕЙ:")
                    print("-" * 30)
                    tree = self.generate_ascii_tree(dependencies, target_package)
                    print(tree)
                else:
                    print("Список зависимостей:", dependencies[target_package])

                # Имитация создания файла с графом
                output_file = self.config["output_filename"]
                print(f"\nГраф зависимостей будет сохранен в: {output_file}")
                print("(В реальной реализации здесь будет создано изображение графа)")

            else:
                print(f"Пакет '{target_package}' не найден в тестовых данных")

            return True

        except Exception as e:
            print(f"ОШИБКА ВЫПОЛНЕНИЯ: {e}", file=sys.stderr)
            return False


def main():
    """Точка входа в приложение"""
    parser = argparse.ArgumentParser(description='Визуализатор графа зависимостей пакетов')
    parser.add_argument('--config', '-c',
                        default='config.json',
                        help='Путь к конфигурационному файлу (по умолчанию: config.json)')

    args = parser.parse_args()

    # Создание и запуск визуализатора
    visualizer = DependencyVisualizer(args.config)
    success = visualizer.run()

    # Завершаем с соответствующим кодом ошибки
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()