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
    "nav.connect": {"az": "Instagram ilə qoşul", "en": "Connect Instagram", "ru": "Подключить Instagram"},
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
        "az": "Instagram ilə davam et",
        "en": "Continue with Instagram",
        "ru": "Продолжить с Instagram",
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
        "az": "Instagram Professional hesabla daxil olun",
        "en": "Sign in with an Instagram Professional account",
        "ru": "Войдите через Instagram Professional",
    },
    "how.2": {
        "az": "Mesaj göndərmə icazəsini verin",
        "en": "Grant message permissions",
        "ru": "Выдайте доступ к сообщениям",
    },
    "how.3": {
        "az": "Qiymət, xidmət və tez-tez verilən sualları sistemə yazın",
        "en": "Fill your Knowledge Base",
        "ru": "Заполните базу знаний",
    },
    "how.4": {
        "az": "Meta webhook-u təsdiqləyin",
        "en": "Confirm the Meta webhook",
        "ru": "Подтвердите Meta webhook",
    },
    "how.5": {
        "az": "Mövzuya aid müştəri DM-lərinə AI cavab versin",
        "en": "Let AI answer on-topic customer DMs",
        "ru": "Пусть ИИ отвечает на релевантные DM",
    },
    "how.cta": {"az": "Instagram ilə başla", "en": "Start with Instagram", "ru": "Начать с Instagram"},
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
        "en": "Knowledge Base",
        "ru": "База знаний",
    },
    "dash.leads": {"az": "Potensial müştərilər", "en": "Leads", "ru": "Лиды"},
    "dash.ai": {"az": "AI Settings", "en": "AI Settings", "ru": "Настройки ИИ"},
    "dash.channels": {"az": "Kanallar", "en": "Channels", "ru": "Каналы"},
    "dash.analytics": {"az": "Analitika", "en": "Analytics", "ru": "Аналитика"},
    "dash.demo": {"az": "AI Demo", "en": "AI Demo", "ru": "AI Демо"},
    "dash.logout": {"az": "Çıxış", "en": "Log out", "ru": "Выйти"},
    "dash.business": {"az": "Biznes", "en": "Business", "ru": "Бизнес"},
    "dash.menu": {"az": "Menu", "en": "Menu", "ru": "Меню"},
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
