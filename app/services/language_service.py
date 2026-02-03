from database.db import db
from typing import Optional
import json


async def get_all_languages():
    """Get all languages"""
    query = "SELECT * FROM languages ORDER BY is_default DESC, name"
    languages = await db.fetch_all(query)
    return [dict(lang) for lang in languages]


async def get_language(language_id: int):
    """Get language by ID"""
    query = "SELECT * FROM languages WHERE id = ?"
    language = await db.fetch_one(query, (language_id,))
    return dict(language) if language else None


async def get_language_by_code(code: str):
    """Get language by code"""
    query = "SELECT * FROM languages WHERE code = ?"
    language = await db.fetch_one(query, (code,))
    return dict(language) if language else None


async def create_language(language_data: dict):
    """Create a new language"""
    query = """
        INSERT INTO languages (code, name, is_active, is_default)
        VALUES (?, ?, ?, ?)
    """
    cursor = await db.execute(
        query,
        (
            language_data['code'],
            language_data['name'],
            language_data.get('is_active', True),
            language_data.get('is_default', False)
        )
    )
    return cursor.lastrowid


async def update_language(language_id: int, language_data: dict):
    """Update language"""
    # If setting as default, unset other defaults first
    if language_data.get('is_default'):
        await db.execute("UPDATE languages SET is_default = 0 WHERE id != ?", (language_id,))
    
    updates = []
    params = []
    
    if 'code' in language_data:
        updates.append("code = ?")
        params.append(language_data['code'])
    if 'name' in language_data:
        updates.append("name = ?")
        params.append(language_data['name'])
    if 'is_active' in language_data:
        updates.append("is_active = ?")
        params.append(language_data['is_active'])
    if 'is_default' in language_data:
        updates.append("is_default = ?")
        params.append(language_data['is_default'])
    
    if updates:
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(language_id)
        query = f"UPDATE languages SET {', '.join(updates)} WHERE id = ?"
        await db.execute(query, tuple(params))
    
    return True


async def delete_language(language_id: int):
    """Delete language and all its translations"""
    # Check if it's the default language
    language = await get_language(language_id)
    if language and language['is_default']:
        return False, "Cannot delete default language"
    
    # Delete language (translations will be deleted via CASCADE)
    query = "DELETE FROM languages WHERE id = ?"
    await db.execute(query, (language_id,))
    return True, "Language deleted successfully"


async def get_translations(language_id: int, category: Optional[str] = None):
    """Get all translations for a language"""
    if category:
        query = "SELECT * FROM translations WHERE language_id = ? AND category = ? ORDER BY key"
        translations = await db.fetch_all(query, (language_id, category))
    else:
        query = "SELECT * FROM translations WHERE language_id = ? ORDER BY category, key"
        translations = await db.fetch_all(query, (language_id,))
    
    return [dict(t) for t in translations]


async def get_translation_by_key(language_id: int, key: str):
    """Get a specific translation"""
    query = "SELECT * FROM translations WHERE language_id = ? AND key = ?"
    translation = await db.fetch_one(query, (language_id, key))
    return dict(translation) if translation else None


async def create_translation(translation_data: dict):
    """Create or update a translation"""
    # Check if translation exists
    existing = await get_translation_by_key(
        translation_data['language_id'],
        translation_data['key']
    )
    
    if existing:
        # Update existing
        query = """
            UPDATE translations 
            SET value = ?, category = ?, updated_at = CURRENT_TIMESTAMP
            WHERE language_id = ? AND key = ?
        """
        await db.execute(
            query,
            (
                translation_data['value'],
                translation_data.get('category', 'general'),
                translation_data['language_id'],
                translation_data['key']
            )
        )
        return existing['id']
    else:
        # Create new
        query = """
            INSERT INTO translations (language_id, key, value, category)
            VALUES (?, ?, ?, ?)
        """
        cursor = await db.execute(
            query,
            (
                translation_data['language_id'],
                translation_data['key'],
                translation_data['value'],
                translation_data.get('category', 'general')
            )
        )
        return cursor.lastrowid


async def update_translation(translation_id: int, translation_data: dict):
    """Update translation"""
    updates = []
    params = []
    
    if 'value' in translation_data:
        updates.append("value = ?")
        params.append(translation_data['value'])
    if 'category' in translation_data:
        updates.append("category = ?")
        params.append(translation_data['category'])
    
    if updates:
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(translation_id)
        query = f"UPDATE translations SET {', '.join(updates)} WHERE id = ?"
        await db.execute(query, tuple(params))
    
    return True


async def bulk_update_translations(language_id: int, translations: dict):
    """Bulk update/create translations for a language"""
    for key, value in translations.items():
        await create_translation({
            'language_id': language_id,
            'key': key,
            'value': value,
            'category': 'general'
        })
    return True


async def delete_translation(translation_id: int):
    """Delete translation"""
    query = "DELETE FROM translations WHERE id = ?"
    await db.execute(query, (translation_id,))
    return True


async def export_language(language_code: str):
    """Export language translations as JSON"""
    # Get language
    language = await get_language_by_code(language_code)
    if not language:
        return None
    
    # Get all translations
    translations = await get_translations(language['id'])
    
    # Format as dictionary
    translations_dict = {}
    for t in translations:
        translations_dict[t['key']] = t['value']
    
    return {
        'code': language['code'],
        'name': language['name'],
        'translations': translations_dict
    }


async def import_language(language_data: dict):
    """Import language from JSON data"""
    # Check if language exists
    existing_lang = await get_language_by_code(language_data['code'])
    
    if existing_lang:
        language_id = existing_lang['id']
        # Update language info
        await update_language(language_id, {
            'name': language_data['name'],
            'is_active': language_data.get('is_active', True)
        })
    else:
        # Create new language
        language_id = await create_language({
            'code': language_data['code'],
            'name': language_data['name'],
            'is_active': language_data.get('is_active', True),
            'is_default': False
        })
    
    # Import translations
    for key, value in language_data['translations'].items():
        await create_translation({
            'language_id': language_id,
            'key': key,
            'value': value,
            'category': 'general'
        })
    
    return language_id


async def get_translation_categories(language_id: int):
    """Get unique categories for a language"""
    query = "SELECT DISTINCT category FROM translations WHERE language_id = ? ORDER BY category"
    categories = await db.fetch_all(query, (language_id,))
    return [c['category'] for c in categories]
