#!/usr/bin/env python
"""
Скрипт для запуска приложения
"""
import os
import sys
import uvicorn

def main():
    """
    Запуск веб-сервера
    """
    print("=== Запуск приложения ===")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main() 