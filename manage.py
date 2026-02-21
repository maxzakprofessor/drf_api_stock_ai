#!/usr/bin/env python
"""Утилита командной строки Django для административных задач."""
import os
import sys

def main():
    """Основная функция для запуска задач администрирования."""
    
    # Сообщаем Django, где искать файл настроек (settings.py) нашего проекта.
    # SkladProject — это название папки, где лежит ваш основной конфиг.
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SkladProject.settings')
    
    try:
        # Пытаемся импортировать системную команду для выполнения задач из терминала
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # Если Django не установлен или виртуальное окружение не активировано, выскочит эта ошибка
        raise ImportError(
            "Не удалось импортировать Django. Вы уверены, что он установлен? "
            "Возможно, вы забыли активировать виртуальное окружение (venv)?"
        ) from exc
        
    # Выполняем команду, которую вы ввели в терминале (например: runserver или migrate)
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    # Запускаем скрипт
    main()
