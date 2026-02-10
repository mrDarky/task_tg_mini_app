// Translation system for mini-app
// Translations can be loaded from API or use hardcoded fallback
let translations = {
    en: {
        // Navigation
        nav_home: 'Home',
        nav_tasks: 'Tasks',
        nav_profile: 'Profile',
        nav_support: 'Support',
        
        // Home page
        welcome_back: 'Welcome back!',
        star_balance: 'Star Balance',
        daily_bonus: 'Daily Bonus',
        claim_bonus: 'Claim your daily reward',
        claim_btn: 'Claim',
        claiming: 'Claiming...',
        streak: 'Streak',
        days: 'days',
        completed_tasks: 'Completed Tasks',
        referrals: 'Referrals',
        quick_tasks: 'Quick Tasks',
        no_tasks_available: 'No tasks available',
        
        // Profile page
        my_profile: 'My Profile',
        member_since: 'Member since',
        your_balance: 'Your Balance',
        total_stars_earned: 'Total stars earned',
        tasks_completed: 'Tasks Completed',
        achievements: 'Achievements',
        total_earned: 'Total Earned',
        star_history: 'Star History (Last 7 Days)',
        achievement_badges: 'Achievement Badges',
        referral_section: 'Referral Program',
        your_referral_code: 'Your Referral Code',
        copy_code: 'Copy Code',
        share_link: 'Share Link',
        invite_friends: 'Invite friends and earn 50 stars for each referral!',
        
        // Tasks page
        available_tasks: 'Available Tasks',
        all_categories: 'All Categories',
        youtube: 'YouTube',
        tiktok: 'TikTok',
        subscribe: 'Subscribe',
        view_details: 'View Details',
        loading: 'Loading...',
        
        // Support page
        support_title: 'Support',
        my_tickets: 'My Tickets',
        no_tickets: 'No tickets yet',
        create_ticket_help: 'Create a ticket to get help from our support team',
        create_new_ticket: 'Create New Ticket',
        ticket_subject: 'Subject',
        ticket_subject_placeholder: 'Brief description of your issue',
        ticket_message: 'Message',
        ticket_message_placeholder: 'Describe your issue in detail...',
        priority: 'Priority',
        priority_low: 'Low',
        priority_medium: 'Medium',
        priority_high: 'High',
        priority_urgent: 'Urgent',
        cancel: 'Cancel',
        submit: 'Submit',
        confirm_submission: 'Confirm Submission',
        confirm_ticket_text: 'Are you sure you want to submit this support ticket?',
        ticket_will_be_sent: 'Your ticket will be sent to our support team for review.',
        cancel: 'Cancel',
        confirm: 'Confirm',
        faq: 'Frequently Asked Questions',
        
        // Messages
        copied_to_clipboard: 'Copied to clipboard!',
        failed_to_copy: 'Failed to copy',
        bonus_claimed: 'Daily bonus claimed!',
        failed_to_claim: 'Failed to claim bonus',
        ticket_submitted: 'Ticket submitted successfully! Our team will respond soon.',
        ticket_failed: 'Failed to submit ticket. Please try again.',
        fill_required_fields: 'Please fill in all required fields',
        form_cleared: 'Form cleared',
        failed_to_load: 'Failed to load data. Please try again.',
        
        // Status
        status_active: 'Active',
        status_open: 'Open',
        status_in_progress: 'In Progress',
        status_resolved: 'Resolved',
        status_closed: 'Closed'
    },
    ru: {
        // Navigation
        nav_home: 'Главная',
        nav_tasks: 'Задачи',
        nav_profile: 'Профиль',
        nav_support: 'Поддержка',
        
        // Home page
        welcome_back: 'С возвращением!',
        star_balance: 'Баланс звёзд',
        daily_bonus: 'Ежедневный бонус',
        claim_bonus: 'Получите ежедневную награду',
        claim_btn: 'Получить',
        claiming: 'Получение...',
        streak: 'Серия',
        days: 'дней',
        completed_tasks: 'Выполненные задачи',
        referrals: 'Рефералы',
        quick_tasks: 'Быстрые задачи',
        no_tasks_available: 'Нет доступных задач',
        
        // Profile page
        my_profile: 'Мой профиль',
        member_since: 'Участник с',
        your_balance: 'Ваш баланс',
        total_stars_earned: 'Всего звёзд заработано',
        tasks_completed: 'Выполнено задач',
        achievements: 'Достижения',
        total_earned: 'Всего заработано',
        star_history: 'История звёзд (последние 7 дней)',
        achievement_badges: 'Значки достижений',
        referral_section: 'Реферальная программа',
        your_referral_code: 'Ваш реферальный код',
        copy_code: 'Копировать код',
        share_link: 'Поделиться ссылкой',
        invite_friends: 'Приглашайте друзей и зарабатывайте 50 звёзд за каждого!',
        
        // Tasks page
        available_tasks: 'Доступные задачи',
        all_categories: 'Все категории',
        youtube: 'YouTube',
        tiktok: 'TikTok',
        subscribe: 'Подписаться',
        view_details: 'Подробнее',
        loading: 'Загрузка...',
        
        // Support page
        support_title: 'Поддержка',
        my_tickets: 'Мои обращения',
        no_tickets: 'Обращений пока нет',
        create_ticket_help: 'Создайте обращение, чтобы получить помощь от нашей службы поддержки',
        create_new_ticket: 'Создать новое обращение',
        ticket_subject: 'Тема',
        ticket_subject_placeholder: 'Краткое описание проблемы',
        ticket_message: 'Сообщение',
        ticket_message_placeholder: 'Опишите вашу проблему подробно...',
        priority: 'Приоритет',
        priority_low: 'Низкий',
        priority_medium: 'Средний',
        priority_high: 'Высокий',
        priority_urgent: 'Срочный',
        cancel: 'Отмена',
        submit: 'Отправить',
        confirm_submission: 'Подтверждение отправки',
        confirm_ticket_text: 'Вы уверены, что хотите отправить это обращение?',
        ticket_will_be_sent: 'Ваше обращение будет отправлено в нашу службу поддержки для рассмотрения.',
        cancel: 'Отмена',
        confirm: 'Подтвердить',
        faq: 'Часто задаваемые вопросы',
        
        // Messages
        copied_to_clipboard: 'Скопировано в буфер обмена!',
        failed_to_copy: 'Не удалось скопировать',
        bonus_claimed: 'Ежедневный бонус получен!',
        failed_to_claim: 'Не удалось получить бонус',
        ticket_submitted: 'Обращение успешно отправлено! Наша команда скоро ответит.',
        ticket_failed: 'Не удалось отправить обращение. Попробуйте еще раз.',
        fill_required_fields: 'Пожалуйста, заполните все обязательные поля',
        form_cleared: 'Форма очищена',
        failed_to_load: 'Не удалось загрузить данные. Попробуйте еще раз.',
        
        // Status
        status_active: 'Активен',
        status_open: 'Открыто',
        status_in_progress: 'В обработке',
        status_resolved: 'Решено',
        status_closed: 'Закрыто'
    },
    es: {
        // Navigation
        nav_home: 'Inicio',
        nav_tasks: 'Tareas',
        nav_profile: 'Perfil',
        nav_support: 'Soporte',
        
        // Home page
        welcome_back: '¡Bienvenido de nuevo!',
        star_balance: 'Balance de estrellas',
        daily_bonus: 'Bono diario',
        claim_bonus: 'Reclama tu recompensa diaria',
        claim_btn: 'Reclamar',
        claiming: 'Reclamando...',
        streak: 'Racha',
        days: 'días',
        completed_tasks: 'Tareas completadas',
        referrals: 'Referencias',
        quick_tasks: 'Tareas rápidas',
        no_tasks_available: 'No hay tareas disponibles',
        
        // Profile page
        my_profile: 'Mi perfil',
        member_since: 'Miembro desde',
        your_balance: 'Tu balance',
        total_stars_earned: 'Total de estrellas ganadas',
        tasks_completed: 'Tareas completadas',
        achievements: 'Logros',
        total_earned: 'Total ganado',
        star_history: 'Historial de estrellas (últimos 7 días)',
        achievement_badges: 'Insignias de logros',
        referral_section: 'Programa de referidos',
        your_referral_code: 'Tu código de referido',
        copy_code: 'Copiar código',
        share_link: 'Compartir enlace',
        invite_friends: '¡Invita amigos y gana 50 estrellas por cada referido!',
        
        // Tasks page
        available_tasks: 'Tareas disponibles',
        all_categories: 'Todas las categorías',
        youtube: 'YouTube',
        tiktok: 'TikTok',
        subscribe: 'Suscribirse',
        view_details: 'Ver detalles',
        loading: 'Cargando...',
        
        // Support page
        support_title: 'Soporte',
        my_tickets: 'Mis tickets',
        no_tickets: 'Aún no hay tickets',
        create_ticket_help: 'Crea un ticket para obtener ayuda de nuestro equipo de soporte',
        create_new_ticket: 'Crear nuevo ticket',
        ticket_subject: 'Asunto',
        ticket_subject_placeholder: 'Breve descripción de tu problema',
        ticket_message: 'Mensaje',
        ticket_message_placeholder: 'Describe tu problema en detalle...',
        priority: 'Prioridad',
        priority_low: 'Baja',
        priority_medium: 'Media',
        priority_high: 'Alta',
        priority_urgent: 'Urgente',
        cancel: 'Cancelar',
        submit: 'Enviar',
        confirm_submission: 'Confirmar envío',
        confirm_ticket_text: '¿Estás seguro de que quieres enviar este ticket de soporte?',
        ticket_will_be_sent: 'Tu ticket será enviado a nuestro equipo de soporte para su revisión.',
        cancel: 'Cancelar',
        confirm: 'Confirmar',
        faq: 'Preguntas frecuentes',
        
        // Messages
        copied_to_clipboard: '¡Copiado al portapapeles!',
        failed_to_copy: 'Error al copiar',
        bonus_claimed: '¡Bono diario reclamado!',
        failed_to_claim: 'Error al reclamar el bono',
        ticket_submitted: '¡Ticket enviado con éxito! Nuestro equipo responderá pronto.',
        ticket_failed: 'Error al enviar el ticket. Por favor, inténtalo de nuevo.',
        fill_required_fields: 'Por favor, completa todos los campos requeridos',
        form_cleared: 'Formulario limpiado',
        failed_to_load: 'Error al cargar datos. Por favor, inténtalo de nuevo.',
        
        // Status
        status_active: 'Activo',
        status_open: 'Abierto',
        status_in_progress: 'En progreso',
        status_resolved: 'Resuelto',
        status_closed: 'Cerrado'
    }
};

// Get current language from localStorage or default to 'en'
function getCurrentLanguage() {
    return localStorage.getItem('miniapp_language') || 'en';
}

// Set current language
function setCurrentLanguage(lang) {
    if (translations[lang]) {
        localStorage.setItem('miniapp_language', lang);
        return true;
    }
    return false;
}

// Get translated text
function t(key) {
    const lang = getCurrentLanguage();
    return translations[lang]?.[key] || translations.en[key] || key;
}

// Translate all elements with data-i18n attribute
function translatePage() {
    const lang = getCurrentLanguage();
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        const text = translations[lang]?.[key] || translations.en[key] || key;
        
        // Update text content or placeholder based on element type
        if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
            if (element.placeholder !== undefined) {
                element.placeholder = text;
            }
        } else if (element.tagName === 'OPTION') {
            element.textContent = text;
        } else {
            element.textContent = text;
        }
    });
}

// Language selector HTML
function createLanguageSelector() {
    const currentLang = getCurrentLanguage();
    const languages = {
        en: '🇬🇧 English',
        ru: '🇷🇺 Русский',
        es: '🇪🇸 Español'
    };
    
    let html = '<div class="dropdown">';
    html += `<button class="btn btn-sm btn-light dropdown-toggle" type="button" id="languageDropdown" data-bs-toggle="dropdown">`;
    html += `<i class="bi bi-translate"></i> ${languages[currentLang]}`;
    html += '</button>';
    html += '<ul class="dropdown-menu dropdown-menu-end">';
    
    for (const [code, name] of Object.entries(languages)) {
        const active = code === currentLang ? 'active' : '';
        html += `<li><a class="dropdown-item ${active}" href="#" data-lang="${code}">${name}</a></li>`;
    }
    
    html += '</ul></div>';
    return html;
}

// Load translations from API
async function loadTranslationsFromAPI(languageCode) {
    try {
        const response = await fetch(`/api/languages/json/${languageCode}`);
        if (response.ok) {
            const data = await response.json();
            if (data && data.translations) {
                translations[languageCode] = data.translations;
                return true;
            }
        }
    } catch (error) {
        console.warn(`Failed to load translations for ${languageCode} from API, using fallback`, error);
    }
    return false;
}

// Initialize translation system
async function initTranslations() {
    // Try to load current language from API
    const currentLang = getCurrentLanguage();
    await loadTranslationsFromAPI(currentLang);
    
    // Translate the page
    translatePage();
    
    // Add language selector to header if it exists
    const header = document.querySelector('.header');
    if (header && !document.getElementById('languageDropdown')) {
        const langSelector = document.createElement('div');
        langSelector.className = 'language-selector';
        langSelector.innerHTML = createLanguageSelector();
        header.appendChild(langSelector);
        
        // Add event listeners to language links
        document.querySelectorAll('[data-lang]').forEach(link => {
            link.addEventListener('click', async (e) => {
                e.preventDefault();
                const newLang = e.target.getAttribute('data-lang');
                if (setCurrentLanguage(newLang)) {
                    // Try to load new language from API
                    await loadTranslationsFromAPI(newLang);
                    // Reload the page to apply new language
                    window.location.reload();
                }
            });
        });
    }
}

// Export functions
window.i18n = {
    t,
    translatePage,
    getCurrentLanguage,
    setCurrentLanguage,
    createLanguageSelector,
    initTranslations,
    loadTranslationsFromAPI
};

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        initTranslations();
    });
} else {
    initTranslations();
}
