"""UI language catalog: Azerbaijani (default), English, Russian."""
from __future__ import annotations

from typing import Any

SUPPORTED_LANGS = ("az", "en", "ru")
DEFAULT_LANG = "az"

LANG_LABELS = {
    "az": "AZ",
    "en": "EN",
    "ru": "RU",
}

# Flat keys → {az, en, ru}
STRINGS: dict[str, dict[str, str]] = {
    "meta.title_landing": {
        "az": "AI Assistant — Instagram AI müştəri asistentı",
        "en": "AI Assistant — Instagram customer messaging",
        "ru": "AI Assistant — AI-помощник для Instagram",
    },
    "nav.features": {"az": "İmkanlar", "en": "Features", "ru": "Возможности"},
    "nav.benefits": {"az": "Faydalar", "en": "Benefits", "ru": "Выгоды"},
    "nav.industries": {"az": "Sahələr", "en": "Industries", "ru": "Отрасли"},
    "nav.how": {"az": "Necə işləyir", "en": "How it works", "ru": "Как это работает"},
    "nav.signin": {"az": "Daxil ol", "en": "Sign in", "ru": "Войти"},
    "nav.connect": {"az": "Qeydiyyat", "en": "Sign up", "ru": "Регистрация"},
    "hero.headline": {
        "az": "Pulunuza və vaxtınıza qənaət edin — daha çox müştəri qazanın.",
        "en": "Save money and time — win more customers.",
        "ru": "Экономьте деньги и время — привлекайте больше клиентов.",
    },
    "hero.tag": {
        "az": "AI Instagram mesajlarını sizin əvəzinizə cavablayır: 24/7, əlavə işçi maaşı olmadan. Tez cavab = daha az itirilmiş müştəri.",
        "en": "AI answers Instagram messages for you 24/7 — without hiring extra staff. Faster replies mean fewer lost customers.",
        "ru": "ИИ отвечает на сообщения Instagram за вас 24/7 — без найма сотрудников. Быстрый ответ = меньше потерянных клиентов.",
    },
    "hero.cta_primary": {
        "az": "Hesab yaradın",
        "en": "Create account",
        "ru": "Создать аккаунт",
    },
    "hero.cta_secondary": {
        "az": "Necə işləyir?",
        "en": "See how it works",
        "ru": "Как это работает?",
    },
    "features.title": {"az": "Nə edir?", "en": "What it does", "ru": "Что делает"},
    "features.lead": {
        "az": "Real Instagram bağlantısı — peşəkar hesabınız, canlı mesajlar, sizin məlumatlarınıza əsasən cavablar.",
        "en": "Real Instagram OAuth — your professional account, live DMs, Knowledge Base answers.",
        "ru": "Настоящий Instagram OAuth — ваш проф. аккаунт, живые DM и ответы из базы знаний.",
    },
    "benefits.title": {
        "az": "Niyə AI Assistant?",
        "en": "Why AI Assistant?",
        "ru": "Почему AI Assistant?",
    },
    "benefits.lead": {
        "az": "Bir alət — üç nəticə: daha az xərc, daha az vaxt itkisi, daha çox satış fürsəti.",
        "en": "One tool — three outcomes: lower cost, less wasted time, more sales opportunities.",
        "ru": "Один инструмент — три результата: меньше затрат, меньше потери времени, больше продаж.",
    },
    "benefit1.title": {"az": "Pulunuza qənaət", "en": "Save money", "ru": "Экономия денег"},
    "benefit1.desc": {
        "az": "Hər mesaj üçün ayrıca operator və ya gecə növbəsi saxlamaq lazım deyil. AI əsas sualları sizin məlumatlarınıza görə cavablayır.",
        "en": "No need to hire extra inbox staff or night shifts. AI handles common questions from your business info.",
        "ru": "Не нужен отдельный оператор на каждое сообщение. ИИ отвечает на типовые вопросы по вашим данным.",
    },
    "benefit2.title": {"az": "Vaxtınıza qənaət", "en": "Save time", "ru": "Экономия времени"},
    "benefit2.desc": {
        "az": "Eyni qiymət və xidmət suallarını təkrar yazmaqdan azad olun. Komandanız real işə — mürəkkəb hallara və satışa fokuslanır.",
        "en": "Stop typing the same price and service answers. Your team focuses on closing deals and complex cases.",
        "ru": "Хватит снова писать одни и те же ответы о цене. Команда фокусируется на сделках и сложных кейсах.",
    },
    "benefit3.title": {"az": "Daha çox müştəri", "en": "Get more customers", "ru": "Больше клиентов"},
    "benefit3.desc": {
        "az": "Tez cavab müştərini gözləməyə qoymur. Potensial alıcılar qeydə alınır — heç bir maraqlı mesaj itib getmir.",
        "en": "Fast replies keep buyers from walking away. Interested customers are captured — no warm lead left waiting.",
        "ru": "Быстрый ответ не даёт клиенту уйти. Заинтересованные покупатели фиксируются — лиды не теряются.",
    },
    "feat1.title": {"az": "Instagram ilə bir klik", "en": "One-click Instagram", "ru": "Instagram в один клик"},
    "feat1.desc": {
        "az": "Biznes hesabınızı Meta OAuth ilə qoşun — şifrə paylaşmadan mesaj icazəsi.",
        "en": "Connect your professional account with Meta OAuth — message access without sharing your password.",
        "ru": "Подключите бизнес-аккаунт через Meta OAuth — доступ к сообщениям без пароля.",
    },
    "feat2.title": {
        "az": "Sizin məlumatlarınıza uyğun cavab",
        "en": "AI replies from your KB",
        "ru": "Ответы ИИ из вашей базы",
    },
    "feat2.desc": {
        "az": "Müştəri Instagram mesajlarına AI sizin əlavə etdiyiniz qiymət, xidmət və tez-tez verilən suallar əsasında, öz üslubunuzla cavab verir.",
        "en": "Customer DMs are answered from your Knowledge Base, in your tone and rules.",
        "ru": "DM клиентов отвечаются по вашей базе знаний, в вашем тоне и правилах.",
    },
    "feat3.title": {
        "az": "Potensial müştəri tutma",
        "en": "Lead detection",
        "ru": "Поиск лидов",
    },
    "feat3.desc": {
        "az": "Müştəri adını və telefonunu yazanda sistem onu avtomatik potensial müştəri kimi qeydə alır — komandanız dərhal görür.",
        "en": "When name and phone appear, a potential customer is logged for your team.",
        "ru": "Когда появляются имя и телефон, лид сохраняется для вашей команды.",
    },
    "feat4.title": {"az": "Vahid idarə paneli", "en": "Unified dashboard", "ru": "Единая панель"},
    "feat4.desc": {
        "az": "Söhbətlər, potensial müştərilər və statistika bir yerdə.",
        "en": "Conversations, leads, and analytics in one place.",
        "ru": "Диалоги, лиды и аналитика в одном месте.",
    },
    "industries.title": {
        "az": "Xidmət biznesləri üçün",
        "en": "Built for service businesses",
        "ru": "Для сервисного бизнеса",
    },
    "industries.lead": {
        "az": "Eyni sistem — cavabları sizin yazdığınız biznes məlumatları müəyyən edir.",
        "en": "Same engine — your Knowledge Base defines the answers.",
        "ru": "Один движок — ответы задаёт ваша база знаний.",
    },
    "ind.construction": {"az": "Tikinti", "en": "Construction", "ru": "Строительство"},
    "ind.medical": {"az": "Tibbi", "en": "Medical", "ru": "Медицина"},
    "ind.restaurant": {"az": "Restoran", "en": "Restaurant", "ru": "Рестораны"},
    "ind.estate": {"az": "Daşınmaz əmlak", "en": "Real estate", "ru": "Недвижимость"},
    "ind.beauty": {"az": "Gözəllik", "en": "Beauty", "ru": "Красота"},
    "ind.legal": {"az": "Hüquq", "en": "Legal", "ru": "Юриспруденция"},
    "ind.education": {"az": "Təhsil", "en": "Education", "ru": "Образование"},
    "how.title": {"az": "Necə işləyir", "en": "How it works", "ru": "Как это работает"},
    "how.lead": {"az": "Bir neçə addımda canlı.", "en": "Live in a few steps.", "ru": "Запуск за несколько шагов."},
    "how.1": {
        "az": "Email ilə hesab yaradın və OTP ilə təsdiqləyin",
        "en": "Create an account with email and verify via OTP",
        "ru": "Создайте аккаунт по email и подтвердите OTP",
    },
    "how.2": {
        "az": "Manual Setup və ya WhatsApp ilə Message Us seçin",
        "en": "Choose Manual Setup or Message Us on WhatsApp",
        "ru": "Выберите Manual Setup или Message Us в WhatsApp",
    },
    "how.3": {
        "az": "Manual yolda Instagram hesabınızı qoşun",
        "en": "On Manual Setup, connect your Instagram account",
        "ru": "В Manual Setup подключите Instagram",
    },
    "how.4": {
        "az": "Biznes məlumatlarını yazın və AI üslubunu seçin",
        "en": "Add business info and choose AI style",
        "ru": "Добавьте данные бизнеса и стиль ИИ",
    },
    "how.5": {
        "az": "AI müştəri suallarına avtomatik cavab versin",
        "en": "Let AI answer customer questions automatically",
        "ru": "Пусть ИИ автоматически отвечает клиентам",
    },
    "how.cta": {"az": "Hesab yaradın", "en": "Create account", "ru": "Создать аккаунт"},
    "footer.blurb": {
        "az": "Vaxta və pula qənaət · daha çox müştəri · Instagram AI.",
        "en": "Save time & money · win more customers · Instagram AI.",
        "ru": "Экономия времени и денег · больше клиентов · Instagram AI.",
    },
    "login.title": {
        "az": "Instagram ilə daxil ol — AI Assistant",
        "en": "Sign in with Instagram — AI Assistant",
        "ru": "Вход через Instagram — AI Assistant",
    },
    "login.lead": {
        "az": "Instagram Professional hesabınızla daxil olun. Şifrənizi bizə vermirsiniz — yalnız Meta OAuth.",
        "en": "Sign in with your Instagram Professional account. You never share your password with us — Meta OAuth only.",
        "ru": "Войдите через Instagram Professional. Пароль нам не нужен — только Meta OAuth.",
    },
    "login.cta": {
        "az": "Instagram ilə daxil ol",
        "en": "Continue with Instagram",
        "ru": "Продолжить с Instagram",
    },
    "dash.dashboard": {"az": "Dashboard", "en": "Dashboard", "ru": "Панель"},
    "dash.conversations": {"az": "Söhbətlər", "en": "Conversations", "ru": "Диалоги"},
    "dash.knowledge": {
        "az": "Biznes məlumatları",
        "en": "Business info",
        "ru": "Данные бизнеса",
    },
    "dash.leads": {"az": "Potensial müştərilər", "en": "Potential customers", "ru": "Потенциальные клиенты"},
    "dash.ai": {"az": "AI üslubu", "en": "AI style", "ru": "Стиль ИИ"},
    "dash.channels": {"az": "Bağlantı", "en": "Connection", "ru": "Подключение"},
    "dash.analytics": {"az": "Analitika", "en": "Analytics", "ru": "Аналитика"},
    "dash.demo": {"az": "AI Demo", "en": "AI Demo", "ru": "AI Демо"},
    "dash.logout": {"az": "Çıxış", "en": "Log out", "ru": "Выйти"},
    "dash.business": {"az": "Biznes", "en": "Business", "ru": "Бизнес"},
    "dash.menu": {"az": "Menu", "en": "Menu", "ru": "Меню"},
    # --- Dashboard page content ---
    "home.title": {"az": "Dashboard", "en": "Dashboard", "ru": "Панель"},
    "home.lead": {
        "az": "bugünkü icmal",
        "en": "today’s overview",
        "ru": "обзор за сегодня",
    },
    "home.kpi_messages": {"az": "Mesajlar (bugün)", "en": "Messages (today)", "ru": "Сообщения (сегодня)"},
    "home.kpi_ai": {"az": "AI cavabları", "en": "AI replies", "ru": "Ответы ИИ"},
    "home.kpi_human": {"az": "İnsan müdaxiləsi", "en": "Human takeover", "ru": "Вмешательство человека"},
    "home.kpi_leads": {"az": "Potensial müştərilər", "en": "Potential customers", "ru": "Потенциальные клиенты"},
    "home.kpi_rate": {"az": "Cavab nisbəti", "en": "Reply rate", "ru": "Доля ответов"},
    "home.kpi_kb": {"az": "Biznes məlumatları", "en": "Business info items", "ru": "Данные бизнеса"},
    "home.recent_convos": {"az": "Son söhbətlər", "en": "Recent conversations", "ru": "Последние диалоги"},
    "home.no_convos": {"az": "Söhbət yoxdur.", "en": "No conversations yet.", "ru": "Диалогов пока нет."},
    "home.view_all": {"az": "Hamısına bax", "en": "View all", "ru": "Смотреть все"},
    "home.quick": {"az": "Tez əməliyyatlar", "en": "Quick actions", "ru": "Быстрые действия"},
    "home.open_demo": {"az": "AI cavabını sına", "en": "Try an AI reply", "ru": "Проверить ответ ИИ"},
    "home.add_kb": {"az": "Biznes məlumatı əlavə et", "en": "Add business info", "ru": "Добавить данные бизнеса"},
    "home.view_leads": {"az": "Potensial müştərilərə bax", "en": "View potential customers", "ru": "Смотреть потенциальных клиентов"},
    "home.onboarding": {"az": "Necə başlamaq", "en": "How to get started", "ru": "Как начать"},
    "home.recent_leads": {"az": "Son potensial müştərilər", "en": "Recent potential customers", "ru": "Недавние потенциальные клиенты"},
    "home.no_leads": {
        "az": "Hələ potensial müştəri yoxdur.",
        "en": "No potential customers yet.",
        "ru": "Потенциальных клиентов пока нет.",
    },
    "home.hot_badge": {"az": "Maraqlı", "en": "Interested", "ru": "Интерес"},
    "conv.title": {"az": "Söhbətlər", "en": "Conversations", "ru": "Диалоги"},
    "conv.lead": {
        "az": "Instagram müştəri söhbətləri — mesajlar və AI cavabları.",
        "en": "Instagram customer chats — messages and AI replies.",
        "ru": "Чаты клиентов Instagram — сообщения и ответы ИИ.",
    },
    "conv.empty": {"az": "Söhbət yoxdur.", "en": "No conversations yet.", "ru": "Диалогов пока нет."},
    "conv.pick": {"az": "Söhbət seçin.", "en": "Select a conversation.", "ru": "Выберите диалог."},
    "kb.title": {"az": "Biznes məlumatları", "en": "Business info", "ru": "Данные бизнеса"},
    "kb.lead": {
        "az": "Qiymət, xidmət və FAQ — AI bu məlumatlara görə cavab verir.",
        "en": "Prices, services, and FAQs — AI answers from this info.",
        "ru": "Цены, услуги и FAQ — ИИ отвечает по этим данным.",
    },
    "kb.new": {"az": "Yeni element", "en": "New item", "ru": "Новый элемент"},
    "kb.type": {"az": "Tip", "en": "Type", "ru": "Тип"},
    "kb.item_title": {"az": "Başlıq", "en": "Title", "ru": "Заголовок"},
    "kb.keywords": {"az": "Açar sözlər (vergüllə)", "en": "Keywords (comma-separated)", "ru": "Ключевые слова (через запятую)"},
    "kb.content": {"az": "Məzmun", "en": "Content", "ru": "Содержание"},
    "kb.add": {"az": "Əlavə et", "en": "Add", "ru": "Добавить"},
    "kb.save": {"az": "Saxla", "en": "Save", "ru": "Сохранить"},
    "kb.delete": {"az": "Sil", "en": "Delete", "ru": "Удалить"},
    "kb.confirm_delete": {"az": "Silinsin?", "en": "Delete this item?", "ru": "Удалить?"},
    "kb.title_ph": {"az": "Məs: Ev tikintisi", "en": "e.g. Home construction", "ru": "Напр.: Строительство дома"},
    "kb.kw_ph": {"az": "qiymət, m2, bakı", "en": "price, m2, baku", "ru": "цена, м2, баку"},
    "kb.type.service": {"az": "Xidmət", "en": "Service", "ru": "Услуга"},
    "kb.type.pricing": {"az": "Qiymət", "en": "Pricing", "ru": "Цены"},
    "kb.type.faq": {"az": "FAQ", "en": "FAQ", "ru": "FAQ"},
    "kb.type.policy": {"az": "Qayda / siyasət", "en": "Policy", "ru": "Политика"},
    "kb.type.business": {"az": "Biznes", "en": "Business", "ru": "Бизнес"},
    "kb.type.document": {"az": "Sənəd", "en": "Document", "ru": "Документ"},
    "leads.title": {"az": "Potensial müştərilər", "en": "Potential customers", "ru": "Потенциальные клиенты"},
    "leads.lead": {
        "az": "Instagram söhbətlərindən toplanan maraqlı müştərilər. Statusu dəyişərək izləyin.",
        "en": "Interesting customers from Instagram chats. Track them by changing status.",
        "ru": "Интересные клиенты из Instagram. Меняйте статус, чтобы отслеживать.",
    },
    "leads.col_name": {"az": "Ad", "en": "Name", "ru": "Имя"},
    "leads.col_contact": {"az": "Əlaqə", "en": "Contact", "ru": "Контакт"},
    "leads.col_intent": {"az": "Maraq", "en": "Interest", "ru": "Интерес"},
    "leads.col_source": {"az": "Haradan", "en": "Source", "ru": "Источник"},
    "leads.col_status": {"az": "Status", "en": "Status", "ru": "Статус"},
    "leads.col_date": {"az": "Tarix", "en": "Date", "ru": "Дата"},
    "leads.empty": {
        "az": "Hələ potensial müştəri yoxdur. Müştəri ad və telefon yazanda burada görünəcək.",
        "en": "No potential customers yet. When someone shares a name and phone, they’ll appear here.",
        "ru": "Потенциальных клиентов пока нет. Когда клиент оставит имя и телефон, они появятся здесь.",
    },
    "leads.status.New": {"az": "Yeni", "en": "New", "ru": "Новый"},
    "leads.status.Contacted": {"az": "Əlaqə saxlanılıb", "en": "Contacted", "ru": "На связи"},
    "leads.status.Qualified": {"az": "Uyğundur", "en": "Qualified", "ru": "Подходит"},
    "leads.status.Converted": {"az": "Müştəri oldu", "en": "Became a customer", "ru": "Стал клиентом"},
    "leads.status.Lost": {"az": "İtirilib", "en": "Lost", "ru": "Потерян"},
    "ai.title": {"az": "AI üslubu", "en": "AI style", "ru": "Стиль ИИ"},
    "ai.lead": {
        "az": "üçün asistent davranışı.",
        "en": "— assistant behavior.",
        "ru": "— поведение ассистента.",
    },
    "ai.name": {"az": "Asistent adı", "en": "Assistant name", "ru": "Имя ассистента"},
    "ai.language": {"az": "Dil", "en": "Language", "ru": "Язык"},
    "ai.tone": {"az": "Ton", "en": "Tone", "ru": "Тон"},
    "ai.length": {"az": "Cavab uzunluğu", "en": "Reply length", "ru": "Длина ответа"},
    "ai.biz_type": {"az": "Biznes tipi", "en": "Business type", "ru": "Тип бизнеса"},
    "ai.rules": {"az": "Qaydalar", "en": "Rules", "ru": "Правила"},
    "ai.save": {"az": "Saxla", "en": "Save", "ru": "Сохранить"},
    "ai.tone.friendly": {"az": "Dostyana", "en": "Friendly", "ru": "Дружелюбный"},
    "ai.tone.professional": {"az": "Peşəkar", "en": "Professional", "ru": "Профессиональный"},
    "ai.tone.formal": {"az": "Rəsmi", "en": "Formal", "ru": "Официальный"},
    "ai.tone.casual": {"az": "Sərbəst", "en": "Casual", "ru": "Свободный"},
    "ai.len.short": {"az": "Qısa", "en": "Short", "ru": "Короткий"},
    "ai.len.medium": {"az": "Orta", "en": "Medium", "ru": "Средний"},
    "ai.len.long": {"az": "Ətraflı", "en": "Detailed", "ru": "Подробный"},
    "ch.title": {"az": "Instagram bağlantısı", "en": "Instagram connection", "ru": "Подключение Instagram"},
    "ch.lead": {
        "az": "Hesabınızı idarə edin və gələn müştəri mesajlarına baxın.",
        "en": "Manage your account and view incoming customer messages.",
        "ru": "Управляйте аккаунтом и смотрите входящие сообщения.",
    },
    "ch.your_account": {"az": "Sizin hesabınız", "en": "Your account", "ru": "Ваш аккаунт"},
    "ch.connected": {"az": "Qoşulub", "en": "Connected", "ru": "Подключено"},
    "ch.disconnected": {"az": "Qoşulmayıb", "en": "Not connected", "ru": "Не подключено"},
    "ch.can_reply": {
        "az": "AI Instagram mesajlarınıza avtomatik cavab verə bilər.",
        "en": "AI can automatically reply to your Instagram messages.",
        "ru": "ИИ может автоматически отвечать на ваши сообщения в Instagram.",
    },
    "ch.connect_hint": {
        "az": "Instagram biznes hesabınızı qoşun ki, AI mesajlara cavab versin.",
        "en": "Connect your Instagram business account so AI can reply to messages.",
        "ru": "Подключите бизнес-аккаунт Instagram, чтобы ИИ отвечал на сообщения.",
    },
    "ch.reconnect": {"az": "Yenidən qoşul", "en": "Reconnect", "ru": "Подключить снова"},
    "ch.refresh": {"az": "Mesaj qəbulunu yenilə", "en": "Refresh message receive", "ru": "Обновить приём сообщений"},
    "ch.disconnect": {"az": "Bağlantını kəs", "en": "Disconnect", "ru": "Отключить"},
    "ch.connect": {"az": "Instagram ilə qoşul", "en": "Connect with Instagram", "ru": "Подключить Instagram"},
    "ch.error": {
        "az": "Bağlantıda problem var. Yenidən qoşulun və ya dəstəyə yazın.",
        "en": "There’s a connection problem. Reconnect or contact support.",
        "ru": "Проблема с подключением. Подключите снова или напишите в поддержку.",
    },
    "ch.recent": {"az": "Son mesajlar", "en": "Recent messages", "ru": "Последние сообщения"},
    "ch.recent_lead": {
        "az": "Instagram-dan gələn son söhbətlər.",
        "en": "Latest chats from Instagram.",
        "ru": "Последние чаты из Instagram.",
    },
    "ch.col_time": {"az": "Vaxt", "en": "Time", "ru": "Время"},
    "ch.col_customer": {"az": "Müştəri", "en": "Customer", "ru": "Клиент"},
    "ch.col_who": {"az": "Kim", "en": "Who", "ru": "Кто"},
    "ch.col_msg": {"az": "Mesaj", "en": "Message", "ru": "Сообщение"},
    "ch.badge_customer": {"az": "Müştəri", "en": "Customer", "ru": "Клиент"},
    "ch.all_convos": {"az": "Bütün söhbətlər", "en": "All conversations", "ru": "Все диалоги"},
    "ch.refresh_page": {"az": "Yenilə", "en": "Refresh", "ru": "Обновить"},
    "ch.empty": {
        "az": "Hələ mesaj yoxdur. Başqa bir Instagram hesabından yazın — cavab burada görünəcək.",
        "en": "No messages yet. Message from another Instagram account — replies will show here.",
        "ru": "Сообщений пока нет. Напишите с другого аккаунта Instagram — ответы появятся здесь.",
    },
    "ch.empty_handle": {
        "az": "biznes profilinizə",
        "en": "your business profile",
        "ru": "вашему бизнес-профилю",
    },
    "ch.tip1": {
        "az": "Başqa hesaba keçin (öz hesabınıza özünüzdən yazmaq olmur)",
        "en": "Use another account (you can’t message yourself)",
        "ru": "Войдите в другой аккаунт (себе писать нельзя)",
    },
    "ch.tip2": {
        "az": "Biznes profilinizə sadə bir sual göndərin",
        "en": "Send a simple question to your business profile",
        "ru": "Отправьте простой вопрос на бизнес-профиль",
    },
    "ch.tip3": {
        "az": "Bu səhifəni yeniləyin və ya Söhbətlər bölməsinə baxın",
        "en": "Refresh this page or open Conversations",
        "ru": "Обновите страницу или откройте Диалоги",
    },
    "ch.coming": {
        "az": "Bu kanal tezliklə əlavə olunacaq.",
        "en": "This channel is coming soon.",
        "ru": "Этот канал скоро появится.",
    },
    "ch.soon": {"az": "Tezliklə", "en": "Coming soon", "ru": "Скоро"},
    "an.title": {"az": "Analitika", "en": "Analytics", "ru": "Аналитика"},
    "an.lead": {
        "az": "mesaj və müştəri statistikası",
        "en": "message and customer stats",
        "ru": "статистика сообщений и клиентов",
    },
    "an.kpi_messages": {"az": "Mesajlar (bugün)", "en": "Messages (today)", "ru": "Сообщения (сегодня)"},
    "an.kpi_ai": {"az": "AI cavabları (ümumi)", "en": "AI replies (total)", "ru": "Ответы ИИ (всего)"},
    "an.kpi_human": {"az": "İnsan müdaxiləsi", "en": "Human takeover", "ru": "Вмешательство человека"},
    "an.kpi_leads": {"az": "Potensial müştərilər", "en": "Potential customers", "ru": "Потенциальные клиенты"},
    "an.kpi_rate": {"az": "Cavab nisbəti", "en": "Reply rate", "ru": "Доля ответов"},
    "an.empty": {
        "az": "Hələ kifayət qədər məlumat yoxdur. Müştərilər yazdıqca qrafiklər dolacaq.",
        "en": "Not enough data yet. Charts will fill as customers message you.",
        "ru": "Пока мало данных. Графики заполнятся, когда клиенты начнут писать.",
    },
    "an.chart_msgs": {"az": "Mesajlar (7 gün)", "en": "Messages (7 days)", "ru": "Сообщения (7 дней)"},
    "an.chart_ai": {"az": "AI və insan cavabları", "en": "AI vs human replies", "ru": "ИИ и ответы человека"},
    "an.chart_funnel": {
        "az": "Potensial müştəri statusları",
        "en": "Potential customer statuses",
        "ru": "Статусы потенциальных клиентов",
    },
    "an.msg_label": {"az": "Mesajlar", "en": "Messages", "ru": "Сообщения"},
    "an.ai_label": {"az": "AI", "en": "AI", "ru": "ИИ"},
    "an.human_label": {"az": "İnsan", "en": "Human", "ru": "Человек"},
    "an.no_data_tip": {"az": "Hələ məlumat yoxdur", "en": "No data yet", "ru": "Пока нет данных"},
    "an.count": {"az": "Say", "en": "Count", "ru": "Кол-во"},
    "an.funnel.New": {"az": "Yeni", "en": "New", "ru": "Новые"},
    "an.funnel.Contacted": {"az": "Əlaqə", "en": "Contacted", "ru": "На связи"},
    "an.funnel.Qualified": {"az": "Uyğun", "en": "Qualified", "ru": "Подходит"},
    "an.funnel.Converted": {"az": "Müştəri", "en": "Customer", "ru": "Клиент"},
    "an.funnel.Lost": {"az": "İtirilib", "en": "Lost", "ru": "Потерян"},
    "onb.title": {"az": "Quraşdırma seçimi", "en": "Choose your setup", "ru": "Выберите настройку"},
    "onb.lead": {
        "az": "Bir neçə dəqiqəyə AI-nizi hazırlayın. Hər addımı bitirəndə işarə avtomatik yenilənir.",
        "en": "Get your AI ready in a few minutes. Steps update automatically as you finish them.",
        "ru": "Подготовьте ИИ за несколько минут. Шаги обновляются автоматически.",
    },
    "onb.done": {"az": "Tamam", "en": "Done", "ru": "Готово"},
    "onb.wait": {"az": "Gözləyir", "en": "Waiting", "ru": "Ожидает"},
    "onb.s1": {"az": "Instagram qoşuldu", "en": "Instagram connected", "ru": "Instagram подключён"},
    "onb.s1d": {
        "az": "Biznes hesabınız bağlandı — AI mesajlara cavab verə bilər.",
        "en": "Your business account is linked — AI can reply to messages.",
        "ru": "Бизнес-аккаунт подключён — ИИ может отвечать на сообщения.",
    },
    "onb.s2": {"az": "Biznes məlumatlarınızı yazın", "en": "Add your business info", "ru": "Добавьте данные бизнеса"},
    "onb.s2d": {
        "az": "Qiymət, xidmətlər və tez-tez verilən sualları əlavə edin ki, AI düzgün cavab versin.",
        "en": "Add prices, services, and FAQs so AI can answer correctly.",
        "ru": "Добавьте цены, услуги и FAQ, чтобы ИИ отвечал правильно.",
    },
    "onb.s3": {"az": "AI üslubunu seçin", "en": "Choose AI style", "ru": "Выберите стиль ИИ"},
    "onb.s3d": {
        "az": "Dil, ton və cavab qaydalarını öz biznesinizə uyğunlaşdırın.",
        "en": "Set language, tone, and reply rules for your business.",
        "ru": "Настройте язык, тон и правила ответов под ваш бизнес.",
    },
    "onb.s4": {"az": "Test mesajı göndərin", "en": "Send a test message", "ru": "Отправьте тестовое сообщение"},
    "onb.s4d": {
        "az": "Başqa bir Instagram hesabından öz biznes profilinizə sadə bir sual yazın.",
        "en": "From another Instagram account, send a simple question to your business profile.",
        "ru": "С другого аккаунта Instagram напишите простой вопрос на бизнес-профиль.",
    },
    "onb.s5": {"az": "Cavabı panelda görün", "en": "See the reply in the panel", "ru": "Посмотрите ответ в панели"},
    "onb.s5d": {
        "az": "Söhbətlər bölməsində müştəri mesajını və AI cavabını izləyin.",
        "en": "Open Conversations to see the customer message and AI reply.",
        "ru": "Откройте Диалоги, чтобы увидеть сообщение клиента и ответ ИИ.",
    },
    "onb.cta_kb": {"az": "Biznes məlumatları", "en": "Business info", "ru": "Данные бизнеса"},
    "onb.cta_ai": {"az": "AI üslubu", "en": "AI style", "ru": "Стиль ИИ"},
    "onb.cta_conv": {"az": "Söhbətlər", "en": "Conversations", "ru": "Диалоги"},
    "hero.kicker": {
        "az": "Instagram · AI · Biznes məlumatları",
        "en": "Instagram · AI · Knowledge Base",
        "ru": "Instagram · AI · База знаний",
    },
    "hero.dm_in": {
        "az": "Salam, Instagram avtomatlaşdırma qiyməti neçəyədir?",
        "en": "Hi, what’s the price for Instagram automation?",
        "ru": "Здравствуйте, сколько стоит автоматизация Instagram?",
    },
    "hero.dm_out": {
        "az": "Aylıq 30 manatdır. Başlamaq istəyirsinizsə yazın.",
        "en": "It’s 30 AZN / month. Want to get started?",
        "ru": "30 манат в месяц. Хотите начать?",
    },
    "hero.dm_label": {
        "az": "AI Assistant cavabı",
        "en": "AI Assistant reply",
        "ru": "Ответ AI Assistant",
    },
    "lang.label": {"az": "Dil", "en": "Language", "ru": "Язык"},
    # --- Auth ---
    "auth.register_title": {"az": "Hesab yaradın", "en": "Create an account", "ru": "Создать аккаунт"},
    "auth.register_lead": {
        "az": "Email və şifrə ilə qeydiyyatdan keçin. Sonra emailinizi OTP ilə təsdiqləyin.",
        "en": "Sign up with email and password. Then verify your email with an OTP code.",
        "ru": "Зарегистрируйтесь по email и паролю. Затем подтвердите почту кодом OTP.",
    },
    "auth.login_title": {"az": "Daxil ol", "en": "Sign in", "ru": "Вход"},
    "auth.login_lead": {
        "az": "Email və şifrənizlə daxil olun.",
        "en": "Sign in with your email and password.",
        "ru": "Войдите с email и паролем.",
    },
    "auth.first_name": {"az": "Ad", "en": "First name", "ru": "Имя"},
    "auth.last_name": {"az": "Soyad", "en": "Last name", "ru": "Фамилия"},
    "auth.email": {"az": "Email", "en": "Email", "ru": "Email"},
    "auth.phone": {"az": "Telefon", "en": "Phone", "ru": "Телефон"},
    "auth.optional": {"az": "istəyə bağlı", "en": "optional", "ru": "необязательно"},
    "auth.password": {"az": "Şifrə", "en": "Password", "ru": "Пароль"},
    "auth.password_confirm": {"az": "Şifrə (təkrar)", "en": "Confirm password", "ru": "Повторите пароль"},
    "auth.register_cta": {"az": "Qeydiyyatdan keç", "en": "Create account", "ru": "Зарегистрироваться"},
    "auth.login_cta": {"az": "Daxil ol", "en": "Sign in", "ru": "Войти"},
    "auth.have_account": {"az": "Artıq hesabınız var?", "en": "Already have an account?", "ru": "Уже есть аккаунт?"},
    "auth.no_account": {"az": "Hesabınız yoxdur?", "en": "No account yet?", "ru": "Нет аккаунта?"},
    "auth.signin_link": {"az": "Daxil ol", "en": "Sign in", "ru": "Войти"},
    "auth.register_link": {"az": "Qeydiyyat", "en": "Sign up", "ru": "Регистрация"},
    "auth.otp_title": {"az": "Email təsdiqi", "en": "Verify your email", "ru": "Подтверждение email"},
    "auth.otp_lead": {
        "az": "6 rəqəmli kodu göndərdik:",
        "en": "We sent a 6-digit code to:",
        "ru": "Мы отправили 6-значный код на:",
    },
    "auth.otp_code": {"az": "OTP kod", "en": "OTP code", "ru": "Код OTP"},
    "auth.otp_cta": {"az": "Təsdiqlə", "en": "Verify", "ru": "Подтвердить"},
    "auth.otp_resend": {"az": "Kodu yenidən göndər", "en": "Resend code", "ru": "Отправить код снова"},
    "auth.otp_wait": {
        "az": "Yenidən göndərmək üçün gözləyin:",
        "en": "Wait before resending:",
        "ru": "Подождите перед повторной отправкой:",
    },
    "onb.hello": {"az": "Salam,", "en": "Hi,", "ru": "Здравствуйте,"},
    "onb.choose_lead": {
        "az": "AI-nizi necə quraşdırmaq istəyirsiniz?",
        "en": "How would you like to set up your AI?",
        "ru": "Как вы хотите настроить ИИ?",
    },
    "onb.manual_title": {"az": "Manual Setup", "en": "Manual Setup", "ru": "Ручная настройка"},
    "onb.manual_desc": {
        "az": "Instagram hesabınızı qoşun və biznes məlumatlarını özünüz əlavə edin.",
        "en": "Connect Instagram and build a more detailed knowledge base yourself, field by field.",
        "ru": "Подключите Instagram и заполните данные бизнеса сами, поле за полем.",
    },
    "onb.manual_note": {
        "az": "Platformanı özünüz idarə etmək üçün uyğundur.",
        "en": "Requires some experience with the platform.",
        "ru": "Подойдёт, если готовы настроить сами.",
    },
    "onb.manual_cta": {"az": "Manual quraşdır", "en": "Set up manually", "ru": "Настроить вручную"},
    "onb.msg_title": {"az": "Message Us", "en": "Message Us", "ru": "Напишите нам"},
    "onb.msg_desc": {
        "az": "Biznes məlumatlarınızı bizə göndərin — hər şeyi sizin üçün ətraflı quraşdıraq.",
        "en": "Send us your business info and we'll help you configure everything in detail ourselves.",
        "ru": "Пришлите данные бизнеса — мы всё подробно настроим за вас.",
    },
    "onb.msg_note": {
        "az": "Bir neçə saat çəkə bilər. WhatsApp açılır.",
        "en": "Takes a couple of hours. Opens WhatsApp.",
        "ru": "Займёт пару часов. Откроется WhatsApp.",
    },
    "onb.msg_cta": {"az": "WhatsApp-da yazın", "en": "Write to us on WhatsApp", "ru": "Написать в WhatsApp"},
}


class Translator:
    """Dot-access helper: t.hero_headline via keys with underscores in templates as t['hero.headline'] or getattr."""

    def __init__(self, lang: str):
        self.lang = normalize_lang(lang)

    def __getitem__(self, key: str) -> str:
        row = STRINGS.get(key) or {}
        return row.get(self.lang) or row.get(DEFAULT_LANG) or key

    def get(self, key: str, default: str = "") -> str:
        row = STRINGS.get(key)
        if not row:
            return default or key
        return row.get(self.lang) or row.get(DEFAULT_LANG) or default or key


def normalize_lang(code: str | None) -> str:
    code = (code or DEFAULT_LANG).lower().strip()
    if code.startswith("az"):
        return "az"
    if code.startswith("en"):
        return "en"
    if code.startswith("ru"):
        return "ru"
    return DEFAULT_LANG


def get_translator(lang: str | None) -> Translator:
    return Translator(normalize_lang(lang))


def localized_choice_pairs(lang: str | None, key_prefix: str, values: list[str]) -> list[tuple[str, str]]:
    """Build (value, label) pairs from STRINGS keys like lead.status.New."""
    tr = get_translator(lang)
    return [(v, tr[f"{key_prefix}.{v}"]) for v in values]


def template_strings(lang: str | None) -> dict[str, str]:
    """Keys with underscores for Django templates: t.nav_features."""
    tr = get_translator(lang)
    return {key.replace(".", "_"): tr[key] for key in STRINGS}


def landing_payload(lang: str | None) -> dict[str, Any]:
    t = get_translator(lang)
    return {
        "benefits": [
            {"title": t["benefit1.title"], "desc": t["benefit1.desc"]},
            {"title": t["benefit2.title"], "desc": t["benefit2.desc"]},
            {"title": t["benefit3.title"], "desc": t["benefit3.desc"]},
        ],
        "features": [
            {"title": t["feat1.title"], "desc": t["feat1.desc"]},
            {"title": t["feat2.title"], "desc": t["feat2.desc"]},
            {"title": t["feat3.title"], "desc": t["feat3.desc"]},
            {"title": t["feat4.title"], "desc": t["feat4.desc"]},
        ],
        "industries": [
            t["ind.construction"],
            t["ind.medical"],
            t["ind.restaurant"],
            t["ind.estate"],
            t["ind.beauty"],
            t["ind.legal"],
            t["ind.education"],
        ],
        "how_steps": [t["how.1"], t["how.2"], t["how.3"], t["how.4"], t["how.5"]],
    }
