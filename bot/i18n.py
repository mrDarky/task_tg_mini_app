"""
Bot translation helper
Load translations from JSON files and provide translation function
"""
import json
from pathlib import Path
from typing import Dict, Optional

# Path to locales directory
LOCALES_DIR = Path(__file__).parent.parent / "locales"

# Cache for loaded translations
_translations_cache: Dict[str, Dict[str, str]] = {}


def load_language(language_code: str) -> Optional[Dict[str, str]]:
    """Load translations for a language from JSON file"""
    if language_code in _translations_cache:
        return _translations_cache[language_code]
    
    json_file = LOCALES_DIR / f"{language_code}.json"
    
    if not json_file.exists():
        return None
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if 'translations' in data:
                _translations_cache[language_code] = data['translations']
                return data['translations']
    except Exception as e:
        print(f"Error loading translations for {language_code}: {e}")
    
    return None


def t(key: str, language_code: str = 'en', **kwargs) -> str:
    """
    Translate a key to the specified language
    
    Args:
        key: Translation key
        language_code: Language code (en, ru, es, etc.)
        **kwargs: Variables to replace in the translation string
    
    Returns:
        Translated string with variables replaced
    """
    translations = load_language(language_code)
    
    if not translations:
        # Fallback to English
        translations = load_language('en')
    
    if not translations or key not in translations:
        return key
    
    text = translations[key]
    
    # Replace variables in the format {variable_name}
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass  # If a variable is missing, just return the text as-is
    
    return text


def reload_translations():
    """Clear translation cache to force reload"""
    global _translations_cache
    _translations_cache = {}
