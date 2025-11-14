#!/usr/bin/env python3
"""
Тестовый скрипт для проверки обработки ошибок
"""

import json
import tempfile
import os
import sys

# Добавляем текущую директорию в путь для импорта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from visualizer import DependencyVisualizer, ConfigError


def run_test(test_name, test_func):
    """Вспомогательная функция для запуска тестов"""
    print(f"\n{test_name}")
    try:
        result = test_func()
        if result:
            print("Тест пройден успешно")
        else:
            print("Тест не прошел")
        return result
    except Exception as e:
        print(f"Ошибка при выполнении теста: {e}")
        return False


def test_valid_config():
    """Тест валидной конфигурации"""
    config = {
        "package_name": "example-package",
        "repository_url": "https://github.com/test/repo",
        "test_repository_mode": False,
        "output_filename": "graph.png",
        "ascii_tree_output": True
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config, f)
        temp_path = f.name

    try:
        visualizer = DependencyVisualizer(temp_path)
        return visualizer.run()
    finally:
        os.unlink(temp_path)


def test_missing_required_param():
    """Тест отсутствия обязательного параметра"""
    config = {
        "repository_url": "https://github.com/test/repo",
        "test_repository_mode": False,
        "output_filename": "graph.png"
        # package_name отсутствует
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config, f)
        temp_path = f.name

    try:
        visualizer = DependencyVisualizer(temp_path)
        # Ожидаем, что run() вернет False при ошибке конфигурации
        result = visualizer.run()
        return not result  # Тест пройден, если run() вернул False (ошибка обработана)
    finally:
        os.unlink(temp_path)


def test_invalid_url():
    """Тест невалидного URL"""
    config = {
        "package_name": "example-package",
        "repository_url": "invalid-url",
        "test_repository_mode": False,
        "output_filename": "graph.png",
        "ascii_tree_output": True
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config, f)
        temp_path = f.name

    try:
        visualizer = DependencyVisualizer(temp_path)
        result = visualizer.run()
        return not result  # Тест пройден, если run() вернул False
    finally:
        os.unlink(temp_path)


def test_test_repo_mode():
    """Тест режима тестового репозитория"""
    config = {
        "package_name": "example-package",
        "repository_url": "https://github.com/test/repo",
        "test_repository_mode": True,
        "output_filename": "graph.png",
        "ascii_tree_output": True
        # test_repository_path отсутствует
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config, f)
        temp_path = f.name

    try:
        visualizer = DependencyVisualizer(temp_path)
        result = visualizer.run()
        return not result  # Тест пройден, если run() вернул False
    finally:
        os.unlink(temp_path)


def test_nonexistent_config_file():
    """Тест несуществующего конфигурационного файла"""
    visualizer = DependencyVisualizer("nonexistent_config.json")
    result = visualizer.run()
    return not result  # Тест пройден, если run() вернул False


def test_invalid_json():
    """Тест невалидного JSON"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write("{ invalid json }")
        temp_path = f.name

    try:
        visualizer = DependencyVisualizer(temp_path)
        result = visualizer.run()
        return not result  # Тест пройден, если run() вернул False
    finally:
        os.unlink(temp_path)


def test_empty_package_name():
    """Тест пустого имени пакета"""
    config = {
        "package_name": "",
        "repository_url": "https://github.com/test/repo",
        "test_repository_mode": False,
        "output_filename": "graph.png",
        "ascii_tree_output": True
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config, f)
        temp_path = f.name

    try:
        visualizer = DependencyVisualizer(temp_path)
        result = visualizer.run()
        return not result  # Тест пройден, если run() вернул False
    finally:
        os.unlink(temp_path)


def test_test_repo_with_nonexistent_path():
    """Тест тестового репозитория с несуществующим путем"""
    config = {
        "package_name": "example-package",
        "repository_url": "https://github.com/test/repo",
        "test_repository_mode": True,
        "test_repository_path": "/nonexistent/path",
        "output_filename": "graph.png",
        "ascii_tree_output": True
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config, f)
        temp_path = f.name

    try:
        visualizer = DependencyVisualizer(temp_path)
        result = visualizer.run()
        return not result  # Тест пройден, если run() вернул False
    finally:
        os.unlink(temp_path)


def test_direct_exception_handling():
    """Тест прямой обработки исключений (без run())"""
    config = {
        "package_name": "example-package",
        "repository_url": "invalid-url",
        "test_repository_mode": False,
        "output_filename": "graph.png"
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config, f)
        temp_path = f.name

    try:
        visualizer = DependencyVisualizer(temp_path)
        visualizer.load_config()
        visualizer.validate_config()  # Должно бросить ConfigError
        return False  # Не должно дойти до этой точки
    except ConfigError:
        return True  # Ожидаемое исключение
    except Exception:
        return False  # Неожиданное исключение
    finally:
        os.unlink(temp_path)


if __name__ == "__main__":
    print("Запуск тестов Dependency Visualizer")
    print("=" * 50)

    tests = [
        ("Валидная конфигурация", test_valid_config),
        ("Отсутствует обязательный параметр", test_missing_required_param),
        ("Невалидный URL", test_invalid_url),
        ("Режим тестового репозитория без пути", test_test_repo_mode),
        ("Несуществующий конфигурационный файл", test_nonexistent_config_file),
        ("Невалидный JSON", test_invalid_json),
        ("Пустое имя пакета", test_empty_package_name),
        ("Тестовый репозиторий с несуществующим путем", test_test_repo_with_nonexistent_path),
        ("Прямая обработка исключений", test_direct_exception_handling),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        if run_test(test_name, test_func):
            passed += 1

    print("\n" + "=" * 50)
    print(f"Результаты: {passed}/{total} тестов пройдено")

    if passed == total:
        print("Все тесты успешно пройдены!")
    else:
        print("Некоторые тесты не пройдены")