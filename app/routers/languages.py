from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import JSONResponse, FileResponse
from app.models import (
    Language, LanguageCreate, LanguageUpdate,
    Translation, TranslationCreate, TranslationUpdate,
    LanguageExport, LanguageImport
)
from app.services import language_service
from app.auth import require_auth
import json
from typing import Optional
from pathlib import Path

router = APIRouter(prefix="/api/languages", tags=["languages"])

# Default mini-app texts (English) used as the baseline for all languages
DEFAULT_MINIAPP_TEXTS = {
    "nav_home": "Home",
    "nav_tasks": "Tasks",
    "nav_profile": "Profile",
    "nav_support": "Support",
    "welcome_back": "Welcome back!",
    "star_balance": "Star Balance",
    "daily_bonus": "Daily Bonus",
    "claim_bonus": "Claim your daily reward",
    "claim_btn": "Claim",
    "claiming": "Claiming...",
    "streak": "Streak",
    "days": "days",
    "completed_tasks": "Completed Tasks",
    "referrals": "Referrals",
    "quick_tasks": "Quick Tasks",
    "no_tasks_available": "No tasks available",
    "my_profile": "My Profile",
    "member_since": "Member since",
    "your_balance": "Your Balance",
    "total_stars_earned": "Total stars earned",
    "tasks_completed": "Tasks Completed",
    "achievements": "Achievements",
    "total_earned": "Total Earned",
    "star_history": "Star History (Last 7 Days)",
    "achievement_badges": "Achievement Badges",
    "referral_section": "Referral Program",
    "your_referral_code": "Your Referral Code",
    "copy_code": "Copy Code",
    "share_link": "Share Link",
    "invite_friends": "Invite friends and earn 50 stars for each referral!",
    "available_tasks": "Available Tasks",
    "all_categories": "All Categories",
    "youtube": "YouTube",
    "tiktok": "TikTok",
    "subscribe": "Subscribe",
    "view_details": "View Details",
    "loading": "Loading...",
    "support_title": "Support",
    "my_tickets": "My Tickets",
    "no_tickets": "No tickets yet",
    "create_ticket_help": "Create a ticket to get help from our support team",
    "create_new_ticket": "Create New Ticket",
    "ticket_subject": "Subject",
    "ticket_subject_placeholder": "Brief description of your issue",
    "ticket_message": "Message",
    "ticket_message_placeholder": "Describe your issue in detail...",
    "priority": "Priority",
    "priority_low": "Low",
    "priority_medium": "Medium",
    "priority_high": "High",
    "priority_urgent": "Urgent",
    "cancel": "Cancel",
    "submit": "Submit",
    "confirm_submission": "Confirm Submission",
    "confirm_ticket_text": "Are you sure you want to submit this support ticket?",
    "ticket_will_be_sent": "Your ticket will be sent to our support team for review.",
    "confirm": "Confirm",
    "faq": "Frequently Asked Questions",
    "copied_to_clipboard": "Copied to clipboard!",
    "failed_to_copy": "Failed to copy",
    "bonus_claimed": "Daily bonus claimed!",
    "failed_to_claim": "Failed to claim bonus",
    "ticket_submitted": "Ticket submitted successfully! Our team will respond soon.",
    "ticket_failed": "Failed to submit ticket. Please try again.",
    "fill_required_fields": "Please fill in all required fields",
    "form_cleared": "Form cleared",
    "failed_to_load": "Failed to load data. Please try again.",
    "status_active": "Active",
    "status_open": "Open",
    "status_in_progress": "In Progress",
    "status_resolved": "Resolved",
    "status_closed": "Closed",
    "bot_welcome_new": "👋 Welcome to Task App, {name}!\n\nComplete tasks and earn stars ⭐\nYour current stars: {stars}\nYour referral link: {referral_link}\n\nShare your link with friends to earn bonus stars!",
    "bot_welcome_back": "👋 Welcome back, {name}!\n\nYour current stars: {stars} ⭐\nYour referral link: {referral_link}",
    "bot_welcome_referred": "🎉 Welcome to Task App, {name}!\n\nYou were referred by a friend who earned {bonus} ⭐!\n\nComplete tasks and earn stars ⭐\nYour current stars: {stars}\nYour referral link: {referral_link}",
    "bot_button_open_app": "🚀 Open Mini App",
    "bot_button_view_tasks": "📋 View Tasks",
    "bot_button_my_profile": "👤 My Profile",
    "bot_button_daily_bonus": "🎁 Daily Bonus",
    "bot_button_help": "ℹ️ Help",
    "bot_button_settings": "⚙️ Settings",
    "bot_button_back": "🔙 Back",
    "bot_task_categories": "📋 *Task Categories*\n\nChoose a category to view available tasks:",
    "bot_profile_title": "👤 *Your Profile*",
    "bot_profile_username": "Username: @{username}",
    "bot_profile_stars": "⭐ Stars: {stars}",
    "bot_profile_completed": "✅ Completed Tasks: {completed}",
    "bot_profile_referrals": "👥 Referrals: {referrals}",
    "bot_profile_achievements": "🏆 Achievements: {achievements}",
    "bot_profile_status": "📌 Status: {status}",
    "bot_profile_member_since": "📅 Member since: {date}",
    "bot_please_start": "Please start the bot first with /start",
    "bot_account_banned": "Your account is banned",
    "bot_no_categories": "No task categories available at the moment.",
}

# Path to locales directory
LOCALES_DIR = Path(__file__).parent.parent.parent / "locales"


@router.get("/", response_model=list[Language])
async def list_languages(username: str = Depends(require_auth)):
    """Get all languages"""
    languages = await language_service.get_all_languages()
    return languages


@router.get("/default-texts", response_model=dict)
async def get_default_texts(username: str = Depends(require_auth)):
    """Get the default mini-app texts (English baseline)"""
    return {"translations": DEFAULT_MINIAPP_TEXTS}


@router.get("/all-texts", response_model=dict)
async def get_all_texts_for_languages(username: str = Depends(require_auth)):
    """Get all languages with their translations for the mini-app texts overview page"""
    languages = await language_service.get_all_languages()
    result = {}
    for lang in languages:
        translations = await language_service.get_translations(lang['id'])
        result[lang['code']] = {
            'id': lang['id'],
            'name': lang['name'],
            'code': lang['code'],
            'is_default': lang['is_default'],
            'is_active': lang['is_active'],
            'translations': {t['key']: {'id': t['id'], 'value': t['value'], 'category': t['category']} for t in translations}
        }
    return result


@router.get("/{language_id}", response_model=Language)
async def get_language(language_id: int, username: str = Depends(require_auth)):
    """Get language by ID"""
    language = await language_service.get_language(language_id)
    if not language:
        raise HTTPException(status_code=404, detail="Language not found")
    return language


@router.post("/", response_model=dict)
async def create_language(language: LanguageCreate, username: str = Depends(require_auth)):
    """Create a new language"""
    # Check if language code already exists
    existing = await language_service.get_language_by_code(language.code)
    if existing:
        raise HTTPException(status_code=400, detail="Language code already exists")
    
    language_id = await language_service.create_language(language.dict())
    return {"id": language_id, "message": "Language created successfully"}


@router.put("/{language_id}", response_model=dict)
async def update_language(language_id: int, language: LanguageUpdate, username: str = Depends(require_auth)):
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
async def delete_language(language_id: int, username: str = Depends(require_auth)):
    """Delete language"""
    success, message = await language_service.delete_language(language_id)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message}


@router.get("/{language_id}/translations", response_model=list[Translation])
async def get_translations(language_id: int, category: Optional[str] = None, username: str = Depends(require_auth)):
    """Get translations for a language"""
    language = await language_service.get_language(language_id)
    if not language:
        raise HTTPException(status_code=404, detail="Language not found")
    
    translations = await language_service.get_translations(language_id, category)
    return translations


@router.get("/{language_id}/categories", response_model=list[str])
async def get_translation_categories(language_id: int, username: str = Depends(require_auth)):
    """Get unique translation categories for a language"""
    language = await language_service.get_language(language_id)
    if not language:
        raise HTTPException(status_code=404, detail="Language not found")
    
    categories = await language_service.get_translation_categories(language_id)
    return categories


@router.post("/translations", response_model=dict)
async def create_translation(translation: TranslationCreate, username: str = Depends(require_auth)):
    """Create or update a translation"""
    translation_id = await language_service.create_translation(translation.dict())
    return {"id": translation_id, "message": "Translation saved successfully"}


@router.put("/translations/{translation_id}", response_model=dict)
async def update_translation(translation_id: int, translation: TranslationUpdate, username: str = Depends(require_auth)):
    """Update translation"""
    await language_service.update_translation(translation_id, translation.dict(exclude_unset=True))
    return {"message": "Translation updated successfully"}


@router.post("/translations/bulk", response_model=dict)
async def bulk_update_translations(language_id: int, translations: dict[str, str], username: str = Depends(require_auth)):
    """Bulk update translations for a language"""
    language = await language_service.get_language(language_id)
    if not language:
        raise HTTPException(status_code=404, detail="Language not found")
    
    await language_service.bulk_update_translations(language_id, translations)
    return {"message": f"Updated {len(translations)} translations"}


@router.delete("/translations/{translation_id}", response_model=dict)
async def delete_translation(translation_id: int, username: str = Depends(require_auth)):
    """Delete translation"""
    await language_service.delete_translation(translation_id)
    return {"message": "Translation deleted successfully"}


@router.get("/export/{language_code}", response_model=LanguageExport)
async def export_language(language_code: str, username: str = Depends(require_auth)):
    """Export language as JSON"""
    data = await language_service.export_language(language_code)
    if not data:
        raise HTTPException(status_code=404, detail="Language not found")
    return data


@router.post("/import", response_model=dict)
async def import_language(language_data: LanguageImport, username: str = Depends(require_auth)):
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
async def import_language_file(file: UploadFile = File(...), username: str = Depends(require_auth)):
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


@router.get("/json/{language_code}")
async def get_language_json(language_code: str):
    """Get language translations as JSON from locales directory"""
    try:
        json_file = LOCALES_DIR / f"{language_code}.json"
        
        if not json_file.exists():
            raise HTTPException(status_code=404, detail=f"Language file for '{language_code}' not found")
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return JSONResponse(content=data)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Invalid JSON format in {language_code}.json: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load language file {language_code}.json: {str(e)}")


@router.post("/{language_id}/generate-defaults", response_model=dict)
async def generate_default_texts(language_id: int, username: str = Depends(require_auth)):
    """Populate a language with the default mini-app texts (only missing keys)"""
    language = await language_service.get_language(language_id)
    if not language:
        raise HTTPException(status_code=404, detail="Language not found")

    # Get existing translation keys for this language
    existing = await language_service.get_translations(language_id)
    existing_keys = {t['key'] for t in existing}

    # Determine category for each key
    def get_category(key: str) -> str:
        if key.startswith("bot_"):
            return "bot"
        if key.startswith("nav_"):
            return "navigation"
        if key.startswith("status_"):
            return "status"
        if key.startswith("priority_"):
            return "support"
        if key.startswith("ticket_") or key in ("support_title", "my_tickets", "no_tickets",
                                                  "create_ticket_help", "create_new_ticket",
                                                  "cancel", "submit", "confirm_submission",
                                                  "confirm_ticket_text", "ticket_will_be_sent",
                                                  "confirm", "faq"):
            return "support"
        return "general"

    added = 0
    for key, value in DEFAULT_MINIAPP_TEXTS.items():
        if key not in existing_keys:
            await language_service.create_translation({
                'language_id': language_id,
                'key': key,
                'value': value,
                'category': get_category(key)
            })
            added += 1

    return {"message": f"Added {added} default translations", "added": added}


@router.post("/{language_id}/auto-translate", response_model=dict)
async def auto_translate_language(
    language_id: int,
    source_language_id: int,
    overwrite: bool = False,
    username: str = Depends(require_auth)
):
    """Auto-translate all texts from source language to target language using Google Translate"""
    target_language = await language_service.get_language(language_id)
    if not target_language:
        raise HTTPException(status_code=404, detail="Target language not found")

    source_language = await language_service.get_language(source_language_id)
    if not source_language:
        raise HTTPException(status_code=404, detail="Source language not found")

    target_code = target_language['code']
    source_code = source_language['code']

    if target_code == source_code:
        raise HTTPException(status_code=400, detail="Source and target languages must be different")

    try:
        from deep_translator import GoogleTranslator
    except ImportError:
        raise HTTPException(status_code=500, detail="Translation library not available. Please install deep-translator.")

    # Get source translations
    source_translations = await language_service.get_translations(source_language_id)
    if not source_translations:
        raise HTTPException(status_code=400, detail="Source language has no translations")

    # Get existing target keys
    existing_target = await language_service.get_translations(language_id)
    existing_keys = {t['key'] for t in existing_target}

    translated_count = 0
    failed_count = 0
    translator = GoogleTranslator(source=source_code, target=target_code)

    for trans in source_translations:
        key = trans['key']
        # Skip if already translated (unless overwrite=True)
        if key in existing_keys and not overwrite:
            continue

        value = trans['value']
        if not value or not value.strip():
            continue

        try:
            translated_value = translator.translate(value)
            if translated_value:
                await language_service.create_translation({
                    'language_id': language_id,
                    'key': key,
                    'value': translated_value,
                    'category': trans.get('category', 'general')
                })
                translated_count += 1
        except Exception:
            failed_count += 1

    return {
        "message": f"Translated {translated_count} texts",
        "translated": translated_count,
        "failed": failed_count
    }
