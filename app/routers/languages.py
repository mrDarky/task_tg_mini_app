from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from app.models import (
    Language, LanguageCreate, LanguageUpdate,
    Translation, TranslationCreate, TranslationUpdate,
    LanguageExport, LanguageImport
)
from app.services import language_service
import json
from typing import Optional

router = APIRouter(prefix="/api/languages", tags=["languages"])


@router.get("/", response_model=list[Language])
async def list_languages():
    """Get all languages"""
    languages = await language_service.get_all_languages()
    return languages


@router.get("/{language_id}", response_model=Language)
async def get_language(language_id: int):
    """Get language by ID"""
    language = await language_service.get_language(language_id)
    if not language:
        raise HTTPException(status_code=404, detail="Language not found")
    return language


@router.post("/", response_model=dict)
async def create_language(language: LanguageCreate):
    """Create a new language"""
    # Check if language code already exists
    existing = await language_service.get_language_by_code(language.code)
    if existing:
        raise HTTPException(status_code=400, detail="Language code already exists")
    
    language_id = await language_service.create_language(language.dict())
    return {"id": language_id, "message": "Language created successfully"}


@router.put("/{language_id}", response_model=dict)
async def update_language(language_id: int, language: LanguageUpdate):
    """Update language"""
    existing = await language_service.get_language(language_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Language not found")
    
    # If updating code, check it's not already used
    if language.code:
        existing_code = await language_service.get_language_by_code(language.code)
        if existing_code and existing_code['id'] != language_id:
            raise HTTPException(status_code=400, detail="Language code already exists")
    
    await language_service.update_language(language_id, language.dict(exclude_unset=True))
    return {"message": "Language updated successfully"}


@router.delete("/{language_id}", response_model=dict)
async def delete_language(language_id: int):
    """Delete language"""
    success, message = await language_service.delete_language(language_id)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message}


@router.get("/{language_id}/translations", response_model=list[Translation])
async def get_translations(language_id: int, category: Optional[str] = None):
    """Get translations for a language"""
    language = await language_service.get_language(language_id)
    if not language:
        raise HTTPException(status_code=404, detail="Language not found")
    
    translations = await language_service.get_translations(language_id, category)
    return translations


@router.get("/{language_id}/categories", response_model=list[str])
async def get_translation_categories(language_id: int):
    """Get unique translation categories for a language"""
    language = await language_service.get_language(language_id)
    if not language:
        raise HTTPException(status_code=404, detail="Language not found")
    
    categories = await language_service.get_translation_categories(language_id)
    return categories


@router.post("/translations", response_model=dict)
async def create_translation(translation: TranslationCreate):
    """Create or update a translation"""
    translation_id = await language_service.create_translation(translation.dict())
    return {"id": translation_id, "message": "Translation saved successfully"}


@router.put("/translations/{translation_id}", response_model=dict)
async def update_translation(translation_id: int, translation: TranslationUpdate):
    """Update translation"""
    await language_service.update_translation(translation_id, translation.dict(exclude_unset=True))
    return {"message": "Translation updated successfully"}


@router.post("/translations/bulk", response_model=dict)
async def bulk_update_translations(language_id: int, translations: dict[str, str]):
    """Bulk update translations for a language"""
    language = await language_service.get_language(language_id)
    if not language:
        raise HTTPException(status_code=404, detail="Language not found")
    
    await language_service.bulk_update_translations(language_id, translations)
    return {"message": f"Updated {len(translations)} translations"}


@router.delete("/translations/{translation_id}", response_model=dict)
async def delete_translation(translation_id: int):
    """Delete translation"""
    await language_service.delete_translation(translation_id)
    return {"message": "Translation deleted successfully"}


@router.get("/export/{language_code}", response_model=LanguageExport)
async def export_language(language_code: str):
    """Export language as JSON"""
    data = await language_service.export_language(language_code)
    if not data:
        raise HTTPException(status_code=404, detail="Language not found")
    return data


@router.post("/import", response_model=dict)
async def import_language(language_data: LanguageImport):
    """Import language from JSON"""
    try:
        language_id = await language_service.import_language(language_data.dict())
        return {
            "id": language_id,
            "message": f"Language '{language_data.name}' imported successfully with {len(language_data.translations)} translations"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to import language")


@router.post("/import-file", response_model=dict)
async def import_language_file(file: UploadFile = File(...)):
    """Import language from JSON file"""
    try:
        content = await file.read()
        language_data = json.loads(content)
        
        # Validate required fields
        if 'code' not in language_data or 'name' not in language_data or 'translations' not in language_data:
            raise HTTPException(status_code=400, detail="Invalid JSON format. Required fields: code, name, translations")
        
        language_id = await language_service.import_language(language_data)
        return {
            "id": language_id,
            "message": f"Language '{language_data['name']}' imported successfully from file"
        }
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to import language file")
