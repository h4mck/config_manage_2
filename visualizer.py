"""
Визуализатор графа зависимостей пакетов
Этап 2: Сбор данных о зависимостях Alpine Linux (apk)
"""

import json
import os
import sys
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional, Set
from pathlib import Path
import argparse
import re


class ConfigError(Exception):
    """Класс для ошибок конфигурации"""
    pass


class DependencyError(Exception):
    """Класс для ошибок получения зависимостей"""
    pass


class AlpinePackageParser:
    """Парсер пакетов Alpine Linux"""

    @staticmethod
    def parse_package_index(content: str) -> Dict[str, Dict[str, Any]]:
        """
        Парсинг индексного файла пакетов Alpine
        Формат: https://wiki.alpinelinux.org/wiki/Apk_spec
        """
        packages = {}
        current_package = {}

        for line in content.splitlines():
            line = line.strip()

            if not line:
                if current_package and 'P' in current_package and 'V' in current_package:
                    pkg_name = f"{current_package['P']}-{current_package['V']}"
                    packages[pkg_name] = current_package.copy()
                current_package = {}
                continue

            if ':' in line:
                key, value = line.split(':', 1)
                current_package[key] = value.strip()

        # Добавляем последний пакет
        if current_package and 'P' in current_package and 'V' in current_package:
            pkg_name = f"{current_package['P']}-{current_package['V']}"
            packages[pkg_name] = current_package.copy()

        return packages

    @staticmethod
    def extract_dependencies(package_data: Dict[str, Any]) -> List[str]:
        """Извлечение зависимостей из данных пакета"""
        dependencies = []

        # Зависимости указываются в поле D
        if 'D' in package_data and package_data['D']:
            deps_str = package_data['D']
            # Зависимости разделены пробелами, могут содержать версии
            for dep in deps_str.split():
                # Убираем условия версий (>, <, = и т.д.)
                clean_dep = re.sub(r'[<=>].*$', '', dep)
                if clean_dep:
                    dependencies.append(clean_dep)

        return dependencies


class DependencyFetcher:
    """Класс для получения зависимостей пакетов"""

    def __init__(self, repository_url: str, test_mode: bool = False, test_path: str = ""):
        self.repository_url = repository_url.rstrip('/')
        self.test_mode = test_mode
        self.test_path = test_path
        self.package_cache: Dict[str, Dict[str, Any]] = {}

    def fetch_package_index(self) -> str:
        """Получение индексного файла пакетов"""
        if self.test_mode:
            return self._fetch_from_test_repository()
        else:
            return self._fetch_from_remote_repository()

    def _fetch_from_test_repository(self) -> str:
        """Получение данных из тестового репозитория"""
        index_path = os.path.join(self.test_path, "APKINDEX.tar.gz")
        if not os.path.exists(index_path):
            # Попробуем найти APKINDEX прямо в директории
            index_path = os.path.join(self.test_path, "APKINDEX")
            if not os.path.exists(index_path):
                raise DependencyError(f"Индексный файл не найден в тестовом репозитории: {self.test_path}")

        try:
            with open(index_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            raise DependencyError(f"Ошибка чтения тестового репозитория: {e}")

    def _fetch_from_remote_repository(self) -> str:
        """Получение данных из удаленного репозитория"""
        index_url = f"{self.repository_url}/APKINDEX.tar.gz"

        try:
            print(f"Загрузка индексного файла: {index_url}")
            with urllib.request.urlopen(index_url) as response:
                # В реальной реализации здесь должна быть распаковка tar.gz
                # Для простоты демонстрации вернем заглушку
                content = response.read().decode('utf-8', errors='ignore')
                return content
        except urllib.error.URLError as e:
            raise DependencyError(f"Ошибка загрузки индексного файла: {e}")
        except Exception as e:
            raise DependencyError(f"Ошибка при получении данных: {e}")

    def get_direct_dependencies(self, package_name: str) -> List[str]:
        """Получение прямых зависимостей пакета"""
        print(f"Поиск пакета: {package_name}")

        # Загружаем индекс пакетов
        index_content = self.fetch_package_index()
        packages = AlpinePackageParser.parse_package_index(index_content)

        # Ищем пакет (может быть указан с версией или без)
        target_package = None

        # Сначала ищем точное совпадение
        for pkg_key, pkg_data in packages.items():
            if pkg_data.get('P') == package_name:
                target_package = pkg_data
                break

        # Если не нашли, ищем по частичному совпадению
        if not target_package:
            for pkg_key, pkg_data in packages.items():
                if package_name in pkg_key:
                    target_package = pkg_data
                    break

        if not target_package:
            raise DependencyError(f"Пакет '{package_name}' не найден в репозитории")

        print(f"Найден пакет: {target_package.get('P')}-{target_package.get('V')}")

        # Извлекаем зависимости
        dependencies = AlpinePackageParser.extract_dependencies(target_package)
        return dependencies


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

    def get_real_dependencies(self) -> List[str]:
        """Получение реальных зависимостей из репозитория Alpine"""
        package_name = self.config["package_name"]
        repository_url = self.config["repository_url"]
        test_mode = self.config.get("test_repository_mode", False)
        test_path = self.config.get("test_repository_path", "")

        fetcher = DependencyFetcher(repository_url, test_mode, test_path)
        dependencies = fetcher.get_direct_dependencies(package_name)

        return dependencies

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

            target_package = self.config["package_name"]

            print(f"\nАНАЛИЗ ПАКЕТА: {target_package}")
            print("=" * 40)

            # Получение реальных зависимостей из репозитория Alpine
            print("Получение зависимостей из репозитория...")
            try:
                direct_dependencies = self.get_real_dependencies()

                print(f"\nПРЯМЫЕ ЗАВИСИМОСТИ ПАКЕТА '{target_package}':")
                print("-" * 40)

                if direct_dependencies:
                    for i, dep in enumerate(direct_dependencies, 1):
                        print(f"{i:2}. {dep}")
                else:
                    print("Прямые зависимости не найдены")

                # Для демонстрации также покажем ASCII-дерево если включен режим
                if self.config.get("ascii_tree_output", False):
                    print(f"\nДЕРЕВО ЗАВИСИМОСТЕЙ (тестовые данные):")
                    print("-" * 40)
                    dependencies = self.generate_sample_dependencies()
                    if target_package in dependencies:
                        tree = self.generate_ascii_tree(dependencies, target_package)
                        print(tree)
                    else:
                        print(f"Пакет '{target_package}' не найден в тестовых данных")

                # Имитация создания файла с графом
                output_file = self.config["output_filename"]
                print(f"\nГраф зависимостей будет сохранен в: {output_file}")
                print("(В реальной реализации здесь будет создано изображение графа)")

            except DependencyError as e:
                print(f"ОШИБКА ПОЛУЧЕНИЯ ЗАВИСИМОСТЕЙ: {e}")
                print("Используются тестовые данные...")

                # Fallback на тестовые данные
                dependencies = self.generate_sample_dependencies()

                if target_package in dependencies:
                    print(f"\nПРЯМЫЕ ЗАВИСИМОСТИ ПАКЕТА '{target_package}' (тестовые данные):")
                    print("-" * 50)
                    for i, dep in enumerate(dependencies[target_package], 1):
                        print(f"{i:2}. {dep}")

                    if self.config.get("ascii_tree_output", False):
                        print(f"\nДЕРЕВО ЗАВИСИМОСТЕЙ:")
                        print("-" * 30)
                        tree = self.generate_ascii_tree(dependencies, target_package)
                        print(tree)
                else:
                    print(f"Пакет '{target_package}' не найден")

            return True

        except Exception as e:
            print(f"ОШИБКА ВЫПОЛНЕНИЯ: {e}", file=sys.stderr)
            return False


def main():
    """Точка входа в приложение"""
    parser = argparse.ArgumentParser(description='Визуализатор графа зависимостей пакетов Alpine Linux')
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