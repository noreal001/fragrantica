#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Конфигурация GoLogin для Fragrantica Parser
Основано на официальной документации: https://gologin.com/docs/api-reference/introduction/quickstart
"""

import os
from typing import Dict, Any

class GoLoginConfig:
    """Конфигурация GoLogin"""
    
    # Основные настройки
    DEFAULT_CONFIG = {
        "token": os.environ.get('GL_API_TOKEN', 'your dev token'),
        "profile_settings": {
            "os": "win",  # Windows OS
            "proxy": "us",  # US прокси
            "fingerprint": "random"  # Случайный fingerprint
        },
        "browser_settings": {
            "headless": False,  # Показывать браузер
            "timeout": 30000,  # Таймаут в миллисекундах
            "viewport": {
                "width": 1920,
                "height": 1080
            }
        },
        "selenium_settings": {
            "implicit_wait": 10,
            "page_load_timeout": 30,
            "script_timeout": 30
        }
    }
    
    # Настройки для разных окружений
    ENVIRONMENTS = {
        "development": {
            "headless": False,
            "timeout": 60000,
            "debug": True
        },
        "production": {
            "headless": True,
            "timeout": 30000,
            "debug": False
        },
        "testing": {
            "headless": True,
            "timeout": 15000,
            "debug": True
        }
    }
    
    @classmethod
    def get_config(cls, environment: str = "development") -> Dict[str, Any]:
        """Получение конфигурации для окружения"""
        config = cls.DEFAULT_CONFIG.copy()
        
        if environment in cls.ENVIRONMENTS:
            env_config = cls.ENVIRONMENTS[environment]
            config["browser_settings"].update(env_config)
        
        return config
    
    @classmethod
    def get_profile_settings(cls) -> Dict[str, Any]:
        """Получение настроек профиля"""
        return cls.DEFAULT_CONFIG["profile_settings"]
    
    @classmethod
    def get_browser_settings(cls) -> Dict[str, Any]:
        """Получение настроек браузера"""
        return cls.DEFAULT_CONFIG["browser_settings"]
    
    @classmethod
    def get_selenium_settings(cls) -> Dict[str, Any]:
        """Получение настроек Selenium"""
        return cls.DEFAULT_CONFIG["selenium_settings"]
    
    @classmethod
    def validate_token(cls) -> bool:
        """Проверка валидности токена"""
        token = os.environ.get('GL_API_TOKEN')
        if not token or token == 'your dev token':
            return False
        return True
    
    @classmethod
    def get_token(cls) -> str:
        """Получение токена"""
        return os.environ.get('GL_API_TOKEN', 'your dev token')

# Экспорт конфигурации
GOLOGIN_CONFIG = GoLoginConfig.get_config()
PROFILE_SETTINGS = GoLoginConfig.get_profile_settings()
BROWSER_SETTINGS = GoLoginConfig.get_browser_settings()
SELENIUM_SETTINGS = GoLoginConfig.get_selenium_settings() 