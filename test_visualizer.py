#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы с зависимостями Alpine
"""

import json
import tempfile
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from visualizer import DependencyVisualizer, AlpinePackageParser, DependencyFetcher


def test_alpine_parser():
    """Тест парсера Alpine пакетов"""
    print("Тест парсера Alpine пакетов")
    print("=" * 40)

    test_index = """
C:Q1W7Dd8KAmO3cXv4n6m9pLs2jRfBhTgY
P:nginx
V:1.24.0-r10
A:x86_64
S:1144421
I:3289088
T:nginx [stable]
U:https://nginx.org/
L:BSD-2-Clause
o:nginx
m:nginx <nginx@example.com>
t:1685432100
c:8a74b3c5d6e7f9a0b1c2d3e4f5a6b7c8d
D:musl libcrypto3 libssl3 pcre2 zlib
p:nginx-doc nginx-mod-http-geoip nginx-mod-http-image-filter nginx-mod-http-xslt-filter nginx-mod-mail nginx-mod-stream
i:nginx

C:Q1a2B3c4D5e6F7g8H9i0Jk1Lm2N3o4P5
P:musl
V:1.2.4-r0
A:x86_64
S:123456
I:456789
T:musl libc
U:https://musl.libc.org/
L:MIT
o:musl
m:musl <musl@example.com>
t:1685432101
c:a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6
D:
p:
i:musl
"""

    packages = AlpinePackageParser.parse_package_index(test_index)
    print(f"Найдено пакетов: {len(packages)}")

    for pkg_name, pkg_data in packages.items():
        print(f"\nПакет: {pkg_name}")
        deps = AlpinePackageParser.extract_dependencies(pkg_data)
        print(f"Зависимости: {deps}")

    return len(packages) == 2


def test_dependency_extraction():
    """Тест извлечения зависимостей"""
    print("\nТест извлечения зависимостей")
    print("=" * 40)

    test_data = {
        'P': 'nginx',
        'V': '1.24.0-r10',
        'D': 'musl libcrypto3>=3.0.0 libssl3 pcre2 zlib'
    }

    dependencies = AlpinePackageParser.extract_dependencies(test_data)
    print(f"Исходные данные: {test_data['D']}")
    print(f"Извлеченные зависимости: {dependencies}")

    expected = ['musl', 'libcrypto3', 'libssl3', 'pcre2', 'zlib']
    return dependencies == expected


def test_dependency_fetcher():
    """Тест DependencyFetcher с тестовыми данными"""
    print("\nТест DependencyFetcher")
    print("=" * 40)

    # Создаем тестовый репозиторий
    test_repo_dir = tempfile.mkdtemp()
    index_content = """C:Q1W7Dd8KAmO3cXv4n6m9pLs2jRfBhTgY
P:test-package
V:1.0.0-r0
D:dep1 dep2>=1.0 dep3
i:test-package

C:R1a2B3c4D5e6F7g8H9i0Jk1Lm2N3o4P5
P:dep1
V:1.0.0-r0
D:
i:dep1
"""

    index_path = os.path.join(test_repo_dir, "APKINDEX")
    with open(index_path, 'w') as f:
        f.write(index_content)

    try:
        fetcher = DependencyFetcher(
            repository_url="https://example.com",
            test_mode=True,
            test_path=test_repo_dir
        )

        dependencies = fetcher.get_direct_dependencies("test-package")
        print(f"Найденные зависимости: {dependencies}")

        expected = ['dep1', 'dep2', 'dep3']
        success = dependencies == expected

        if success:
            print("✓ Зависимости успешно извлечены")
        else:
            print(f"✗ Ожидалось: {expected}, получено: {dependencies}")

        return success

    except Exception as e:
        print(f"✗ Ошибка: {e}")
        return False
    finally:
        import shutil
        shutil.rmtree(test_repo_dir)


def test_real_config():
    """Тест с реальной конфигурацией Alpine"""
    print("\nТест с реальной конфигурацией Alpine")
    print("=" * 40)

    config = {
        "package_name": "nginx",
        "repository_url": "https://dl-cdn.alpinelinux.org/alpine/v3.18/main",
        "test_repository_mode": False,  # Исправлено: False вместо false
        "output_filename": "test_output.png",
        "ascii_tree_output": True  # Исправлено: True вместо true
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config, f)
        temp_path = f.name

    try:
        visualizer = DependencyVisualizer(temp_path)
        result = visualizer.run()
        return result
    except Exception as e:
        print(f"Ошибка при выполнении: {e}")
        return False
    finally:
        os.unlink(temp_path)


def test_test_repository():
    """Тест с тестовым репозиторием"""
    print("\nТест с тестовым репозиторием")
    print("=" * 40)

    # Создаем тестовый репозиторий
    test_repo_dir = tempfile.mkdtemp()
    index_content = """C:Q1W7Dd8KAmO3cXv4n6m9pLs2jRfBhTgY
P:test-package
V:1.0.0-r0
D:dep1 dep2>=1.0 dep3
i:test-package

C:R1a2B3c4D5e6F7g8H9i0Jk1Lm2N3o4P5
P:dep1
V:1.0.0-r0
D:
i:dep1

C:S2b3C4d5E6f7G8h9I0jK1lM2nO3p4Q5r
P:another-package
V:2.0.0-r1
D:test-package libc
i:another-package
"""

    index_path = os.path.join(test_repo_dir, "APKINDEX")
    with open(index_path, 'w') as f:
        f.write(index_content)

    config = {
        "package_name": "test-package",
        "repository_url": "https://example.com",
        "test_repository_mode": True,  # Исправлено: True вместо true
        "test_repository_path": test_repo_dir,
        "output_filename": "test_output.png",
        "ascii_tree_output": False  # Исправлено: False вместо false
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config, f)
        temp_path = f.name

    try:
        visualizer = DependencyVisualizer(temp_path)
        result = visualizer.run()
        return result
    except Exception as e:
        print(f"Ошибка при выполнении: {e}")
        return False
    finally:
        import shutil
        shutil.rmtree(test_repo_dir)
        os.unlink(temp_path)


def test_complex_dependencies():
    """Тест сложных случаев зависимостей"""
    print("\nТест сложных случаев зависимостей")
    print("=" * 40)

    test_cases = [
        {
            'name': 'Простые зависимости',
            'input': 'lib1 lib2 lib3',
            'expected': ['lib1', 'lib2', 'lib3']
        },
        {
            'name': 'Зависимости с версиями',
            'input': 'lib1>=1.0 lib2<2.0 lib3=3.0',
            'expected': ['lib1', 'lib2', 'lib3']
        },
        {
            'name': 'Смешанные зависимости',
            'input': 'lib1 lib2>=1.0 lib3<2.0 lib4=3.0 lib5',
            'expected': ['lib1', 'lib2', 'lib3', 'lib4', 'lib5']
        },
        {
            'name': 'Пустые зависимости',
            'input': '',
            'expected': []
        },
        {
            'name': 'Зависимости с пробелами',
            'input': '  lib1  lib2>=1.0  lib3  ',
            'expected': ['lib1', 'lib2', 'lib3']
        }
    ]

    all_passed = True

    for test_case in test_cases:
        package_data = {'D': test_case['input']}
        result = AlpinePackageParser.extract_dependencies(package_data)

        if result == test_case['expected']:
            print(f"✓ {test_case['name']}: {result}")
        else:
            print(f"✗ {test_case['name']}: ожидалось {test_case['expected']}, получено {result}")
            all_passed = False

    return all_passed


def test_package_parsing_edge_cases():
    """Тест граничных случаев парсинга пакетов"""
    print("\nТест граничных случаев парсинга")
    print("=" * 40)

    edge_cases = [
        # Пустой файл
        ("", 0),
        # Только пробелы
        ("   \n  \n  ", 0),
        # Пакет без зависимостей
        ("P:test\nV:1.0\nD:\ni:test", 1),
        # Пакет с пробелами в значениях
        ("P: test-package \nV: 1.0.0 \nD: dep1 dep2 \ni: test-package ", 1),
    ]

    all_passed = True

    for i, (index_content, expected_count) in enumerate(edge_cases):
        try:
            packages = AlpinePackageParser.parse_package_index(index_content)
            if len(packages) == expected_count:
                print(f"Случай {i + 1}: найдено {len(packages)} пакетов")
            else:
                print(f"Случай {i + 1}: ожидалось {expected_count}, найдено {len(packages)}")
                all_passed = False
        except Exception as e:
            print(f"Случай {i + 1}: ошибка {e}")
            all_passed = False

    return all_passed


if __name__ == "__main__":
    print("Тестирование системы зависимостей Alpine Linux")
    print("=" * 50)

    tests = [
        ("Парсер Alpine пакетов", test_alpine_parser),
        ("Извлечение зависимостей", test_dependency_extraction),
        ("Сложные случаи зависимостей", test_complex_dependencies),
        ("Граничные случаи парсинга", test_package_parsing_edge_cases),
        ("DependencyFetcher", test_dependency_fetcher),
        ("Тестовый репозиторий", test_test_repository),
        ("Реальная конфигурация", test_real_config),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n{test_name}")
        print("-" * 40)
        try:
            if test_func():
                print("Тест пройден успешно")
                passed += 1
            else:
                print("Тест не прошел")
        except Exception as e:
            print(f"Ошибка при выполнении теста: {e}")
            import traceback

            traceback.print_exc()

    print("\n" + "=" * 50)
    print(f"Результаты: {passed}/{total} тестов пройдено")

    if passed == total:
        print("Все тесты успешно пройдены!")
    else:
        print("Некоторые тесты не пройдены")