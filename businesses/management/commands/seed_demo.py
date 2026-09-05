"""Seed demo data for AI Assistant multi-tenant demo."""
from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from ai.models import AISettings
from analytics.models import AnalyticsSnapshot
from businesses.models import Business, BusinessType
from channels.models import Channel, ChannelStatus, ChannelType
from conversations.models import Conversation, ConversationStatus, Message, MessageLabel, MessageSender
from knowledge.models import KnowledgeItem, KnowledgeType
from leads.models import Lead, LeadSource, LeadStatus


class Command(BaseCommand):
    help = "DEPRECATED: seed mock demo data. Prefer Instagram OAuth. Use clear_mock_data to remove."

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.WARNING(
                "seed_demo creates MOCK tenants. Prefer Instagram OAuth login. "
                "Continuing anyway..."
            )
        )
        self._clear()
        businesses = self._seed_businesses()
        self._seed_ai_settings(businesses)
        self._seed_knowledge(businesses)
        self._seed_channels(businesses)
        self._seed_conversations_and_leads(businesses)
        self._seed_analytics(businesses)
        self.stdout.write(self.style.SUCCESS("Demo data ready. Default business: abc-construction"))

    def _clear(self):
        AnalyticsSnapshot.objects.all().delete()
        Lead.objects.all().delete()
        Message.objects.all().delete()
        Conversation.objects.all().delete()
        Channel.objects.all().delete()
        KnowledgeItem.objects.all().delete()
        AISettings.objects.all().delete()
        Business.objects.all().delete()

    def _seed_businesses(self) -> dict[str, Business]:
        data = [
            {
                "id": "abc-construction",
                "name": "ABC Construction",
                "type": BusinessType.CONSTRUCTION,
                "description": "Bakı və ətrafında ev tikintisi, villa və təmir xidmətləri.",
                "city": "Bakı",
                "phone": "+994 12 345 67 89",
                "working_hours": "Bazar ertəsi–Şənbə 09:00–18:00",
                "service_areas": ["Bakı", "Xırdalan", "Sumqayıt"],
                "speciality": ["Ev tikintisi", "Villa", "Təmir", "Fasad"],
            },
            {
                "id": "dr-aysel-clinic",
                "name": "Dr. Aysel Medical Clinic",
                "type": BusinessType.MEDICAL,
                "description": "Dermatologiya və dəri sağlamlığı klinikası.",
                "city": "Bakı",
                "phone": "+994 12 555 44 33",
                "working_hours": "Bazar ertəsi–Cümə 10:00–19:00",
                "service_areas": ["Bakı"],
                "speciality": ["Dermatologiya", "Lazer", "Estetik"],
            },
            {
                "id": "urban-table",
                "name": "Urban Table",
                "type": BusinessType.RESTAURANT,
                "description": "Müasir mətbəx, rezervasiya və catering.",
                "city": "Bakı",
                "phone": "+994 12 400 20 20",
                "working_hours": "Hər gün 12:00–23:00",
                "service_areas": ["Bakı"],
                "cuisine": ["Avropa", "Azərbaycan", "Fusion"],
            },
            {
                "id": "prime-estate",
                "name": "Prime Estate",
                "type": BusinessType.REAL_ESTATE,
                "description": "Satış və kirayə üzrə daşınmaz əmlak agentliyi.",
                "city": "Bakı",
                "phone": "+994 12 310 10 10",
                "working_hours": "Bazar ertəsi–Şənbə 10:00–19:00",
                "service_areas": ["Bakı", "Xırdalan"],
                "speciality": ["Mənzil", "Ofis", "Torpaq"],
            },
        ]
        out = {}
        for row in data:
            out[row["id"]] = Business.objects.create(**row)
        return out

    def _seed_ai_settings(self, businesses: dict[str, Business]):
        rules = {
            "abc-construction": (
                "Qiymətləri Knowledge Base-dən götür. Xidmət əraziləri: Bakı, Xırdalan, Sumqayıt. "
                "Sahə (m²) varsa təxmini qiymət hesabla. Salam ilə gələn suallarda salamlama FAQ-ını "
                "substantiv cavaba qurban etmə."
            ),
            "dr-aysel-clinic": (
                "Tibbi diaqnoz və dərman/resept vermə. Təhlükəli tibbi məsləhət üçün insan həkimə yönləndir. "
                "Yalnız qəbul saatları, xidmətlər və ümumi məlumat ver."
            ),
            "urban-table": (
                "Rezervasiya üçün tarix, saat və qonaq sayı soruş. Menyu və allergiya suallarında KB-dən cavab ver."
            ),
            "prime-estate": (
                "Əmlak sorğusunda otaq sayı, rayon və kirayə/satış niyyətini soruş. Qiymət aralığını KB-dən ver."
            ),
        }
        names = {
            "abc-construction": "ABC Assistant",
            "dr-aysel-clinic": "Klinik Asistent",
            "urban-table": "Urban Host",
            "prime-estate": "Prime Guide",
        }
        for bid, biz in businesses.items():
            AISettings.objects.create(
                business=biz,
                assistant_name=names[bid],
                language="az",
                tone="friendly" if bid != "dr-aysel-clinic" else "professional",
                response_length="medium",
                business_type=biz.type,
                rules=rules[bid],
            )

    def _seed_knowledge(self, businesses: dict[str, Business]):
        abc = businesses["abc-construction"]
        abc_items = [
            (
                KnowledgeType.BUSINESS,
                "Şirkət haqqında",
                "ABC Construction Bakıda fəaliyyət göstərən tikinti şirkətidir. "
                "Ev tikintisi, villa, təmir və fasad işləri görürük.",
                ["abc", "şirkət", "haqqında"],
            ),
            (
                KnowledgeType.SERVICE,
                "Ev tikintisi",
                "Ev tikintisi 800 AZN/m². Açara təhvil standartına qədər tam tikinti paketi.",
                ["ev", "tikinti", "qiymət", "800", "m²", "m2"],
            ),
            (
                KnowledgeType.SERVICE,
                "Villa tikintisi",
                "Villa tikintisi 850 AZN/m². Fərdi layihə və premium material seçimləri mövcuddur.",
                ["villa", "tikinti", "850", "qiymət"],
            ),
            (
                KnowledgeType.SERVICE,
                "Təmir",
                "Təmir xidməti 250 AZN/m². Kosmetik və kapital təmir paketləri.",
                ["təmir", "temir", "250", "qiymət"],
            ),
            (
                KnowledgeType.SERVICE,
                "Fasad",
                "Fasad işləri 120 AZN/m². İzolasiya və dekorativ örtük daxildir.",
                ["fasad", "120", "qiymət"],
            ),
            (
                KnowledgeType.BUSINESS,
                "Xidmət əraziləri",
                "Xidmət əraziləri: Bakı, Xırdalan, Sumqayıt.",
                ["ərazi", "bakı", "xırdalan", "sumqayıt", "harada"],
            ),
            (
                KnowledgeType.FAQ,
                "Xırdalanda işləyirsiniz?",
                "Bəli, Xırdalanda işləyirik.",
                ["xırdalan", "xirdalan", "işləyirsiniz", "ərazi"],
            ),
            (
                KnowledgeType.FAQ,
                "Salam / Xoş gəlmisiniz",
                "Salam! ABC Construction-a xoş gəlmisiniz. Ev tikintisi, villa və təmir haqqında sualınızı yazın.",
                ["salam", "xoş gəlmisiniz", "greeting", "salamlama"],
            ),
            (
                KnowledgeType.FAQ,
                "Qəbələdə işləyirsiniz?",
                "Hazırda əsas xidmət ərazilərimiz Bakı, Xırdalan və Sumqayıtdır. "
                "Qəbələ üzrə layihələr fərdi qiymətləndirmə tələb edir.",
                ["qəbələ", "qebale", "ərazi"],
            ),
            (
                KnowledgeType.FAQ,
                "500 m² villa",
                "Böyük villa layihələri (məs. 500 m²) fərdi smeta ilə hazırlanır. "
                "Baza tarif villa üçün 850 AZN/m²-dir; Qəbələ kimi uzaq ərazilərdə əlavə xərclər ola bilər.",
                ["500", "villa", "qəbələ"],
            ),
            (
                KnowledgeType.FAQ,
                "200 m² ev qiyməti",
                "200 m² ev tikintisi üçün təxmini məbləğ 160.000 AZN-dir (200 × 800 AZN/m²).",
                ["200", "qiymət", "ev", "160000", "hesabla"],
            ),
            (
                KnowledgeType.FAQ,
                "Ödəniş qaydası",
                "Ödəniş adətən mərhələli aparılır: müqavilə 30%, karkas 40%, təhvil 30%. "
                "Bank köçürməsi və rəsmi müqavilə tətbiq olunur.",
                ["ödəniş", "pul", "ödeme", "müqavilə"],
            ),
            (
                KnowledgeType.FAQ,
                "Zəmanət",
                "Konstrukiv işlərə 5 il, bitirmə işlərinə 1 il zəmanət veririk.",
                ["zəmanət", "zemanet", "garantiya"],
            ),
            (
                KnowledgeType.FAQ,
                "Tikinti müddəti",
                "Standart 150–200 m² ev orta hesabla 6–9 ay çəkir (hava və icazələrdən asılı).",
                ["müddət", "muddet", "nə qədər", "vaxt", "ne qeder"],
            ),
            (
                KnowledgeType.POLICY,
                "Başlama proseduru",
                "Başlamaq üçün ölçü/sahə, ərazi və əlaqə məlumatı lazımdır. "
                "Ad, soyad və +994 telefonu yazın — sizi potensial müştəri kimi qeydə alarıq.",
                ["başlamaq", "baslamaq", "müraciət", "prosedur"],
            ),
        ]
        for t, title, content, kw in abc_items:
            KnowledgeItem.objects.create(business=abc, type=t, title=title, content=content, keywords=kw)

        clinic = businesses["dr-aysel-clinic"]
        for t, title, content, kw in [
            (
                KnowledgeType.BUSINESS,
                "Klinik haqqında",
                "Dr. Aysel Medical Clinic dermatologiya və estetik dəri baxımı üzrə ixtisaslaşır.",
                ["klinika", "dermatologiya", "aysel"],
            ),
            (
                KnowledgeType.SERVICE,
                "Dermatoloji müayinə",
                "İlkin dermatoloji müayinə 60 AZN. Qəbul onlayn və ya telefonla yazılır.",
                ["müayinə", "qiymət", "qəbul"],
            ),
            (
                KnowledgeType.SERVICE,
                "Lazer epilyasiya",
                "Lazer epilyasiya seansları zonaya görə 40–150 AZN.",
                ["lazer", "epilyasiya"],
            ),
            (
                KnowledgeType.FAQ,
                "Qəbul saatları",
                "Qəbul: Bazar ertəsi–Cümə 10:00–19:00. Təcili hallarda növbədə gözləyin.",
                ["saat", "qəbul", "iş saatı"],
            ),
            (
                KnowledgeType.POLICY,
                "Tibbi məsləhət qaydası",
                "Onlayn diaqnoz və dərman tövsiyəsi verilmir. Şəxsi müayinə üçün həkimə yönləndirilir.",
                ["diaqnoz", "dərman", "resept", "qayda"],
            ),
            (
                KnowledgeType.FAQ,
                "Salam",
                "Salam! Dr. Aysel klinikasının AI köməkçisiyəm. Qəbul və xidmətlər barədə yazın.",
                ["salam", "xoş gəlmisiniz"],
            ),
        ]:
            KnowledgeItem.objects.create(business=clinic, type=t, title=title, content=content, keywords=kw)

        restaurant = businesses["urban-table"]
        for t, title, content, kw in [
            (
                KnowledgeType.BUSINESS,
                "Restoran haqqında",
                "Urban Table — Avropa və Azərbaycan fusion mətbəxi. Canlı musiqi cümə-şənbə.",
                ["restoran", "urban"],
            ),
            (
                KnowledgeType.SERVICE,
                "Rezervasiya",
                "Rezervasiya üçün tarix, saat və qonaq sayı lazımdır. 8+ nəfər üçün depozit tələb oluna bilər.",
                ["rezerv", "bron", "masa"],
            ),
            (
                KnowledgeType.FAQ,
                "Menyu",
                "Günün menyusu və vegetarian seçimlər mövcuddur. Allergiyanızı əvvəlcədən bildirin.",
                ["menyu", "yemək", "vegetarian"],
            ),
            (
                KnowledgeType.FAQ,
                "İş saatları",
                "Hər gün 12:00–23:00 açıqıq. Mətbəx son sifarişi 22:30-da qəbul edir.",
                ["saat", "açıq"],
            ),
            (
                KnowledgeType.FAQ,
                "Salam",
                "Salam! Urban Table-ə xoş gəlmisiniz. Rezervasiya və ya menyu üçün yazın.",
                ["salam", "xoş gəlmisiniz"],
            ),
        ]:
            KnowledgeItem.objects.create(business=restaurant, type=t, title=title, content=content, keywords=kw)

        estate = businesses["prime-estate"]
        for t, title, content, kw in [
            (
                KnowledgeType.BUSINESS,
                "Agentlik haqqında",
                "Prime Estate Bakıda satış və kirayə mənzil/ofis portfeli idarə edir.",
                ["prime", "əmlak", "agentlik"],
            ),
            (
                KnowledgeType.SERVICE,
                "Kirayə mənzillər",
                "2 otaqlı mərkəz mənzilləri 800–1400 AZN/ay. Nəsimi və Nərimanov aktivdir.",
                ["kirayə", "mənzil", "2 otaq"],
            ),
            (
                KnowledgeType.SERVICE,
                "Satış",
                "Yeni tikili 1–3 otaq: 1800–2800 AZN/m² (layihədən asılı).",
                ["satış", "qiymət", "m²"],
            ),
            (
                KnowledgeType.FAQ,
                "Necə axtarım?",
                "Otaq sayı, rayon və kirayə/satış niyyətinizi yazın — uyğun elanları seçək.",
                ["axtarış", "otaq", "rayon"],
            ),
            (
                KnowledgeType.FAQ,
                "Salam",
                "Salam! Prime Estate köməkçisiyəm. Axtardığınız əmlakı təsvir edin.",
                ["salam", "xoş gəlmisiniz"],
            ),
        ]:
            KnowledgeItem.objects.create(business=estate, type=t, title=title, content=content, keywords=kw)

    def _seed_channels(self, businesses: dict[str, Business]):
        handles = {
            "abc-construction": "@abc.construction.az",
            "dr-aysel-clinic": "@draysel.clinic",
            "urban-table": "@urbantable.baku",
            "prime-estate": "@primeestate.az",
        }
        for bid, biz in businesses.items():
            Channel.objects.create(
                business=biz,
                type=ChannelType.INSTAGRAM,
                status=ChannelStatus.CONNECTED if bid == "abc-construction" else ChannelStatus.DISCONNECTED,
                handle=handles[bid],
            )
            Channel.objects.create(
                business=biz,
                type=ChannelType.WHATSAPP,
                status=ChannelStatus.COMING_SOON,
                handle=biz.phone,
            )
            Channel.objects.create(
                business=biz,
                type=ChannelType.WEBSITE,
                status=ChannelStatus.COMING_SOON,
                handle=f"https://{bid}.example.az",
            )

    def _seed_conversations_and_leads(self, businesses: dict[str, Business]):
        now = timezone.now()

        # ABC conversations
        abc = businesses["abc-construction"]
        c1 = Conversation.objects.create(
            business=abc,
            customer_name="Elvin Quliyev",
            channel="instagram",
            status=ConversationStatus.AI,
            lead_potential=True,
            updated_at=now - timedelta(hours=2),
        )
        Message.objects.create(
            conversation=c1,
            sender=MessageSender.CUSTOMER,
            content="Salam, 150 m² ev tikmək istəyirəm. Sumqayıtda işləyirsiniz?",
            timestamp=now - timedelta(hours=2, minutes=10),
        )
        Message.objects.create(
            conversation=c1,
            sender=MessageSender.AI,
            content="Bəli, Sumqayıtda işləyirik. 150 m² üçün təxmini qiymət 120.000 AZN (800 AZN/m²).",
            label=MessageLabel.AI_ANSWERED,
            timestamp=now - timedelta(hours=2, minutes=9),
        )
        Message.objects.create(
            conversation=c1,
            sender=MessageSender.CUSTOMER,
            content="Başlamaq istəyirəm.",
            label=MessageLabel.LEAD,
            timestamp=now - timedelta(hours=2, minutes=5),
        )

        c2 = Conversation.objects.create(
            business=abc,
            customer_name="Nigar Həsənova",
            channel="whatsapp",
            status=ConversationStatus.HUMAN,
            lead_potential=False,
            updated_at=now - timedelta(hours=5),
        )
        Message.objects.create(
            conversation=c2,
            sender=MessageSender.CUSTOMER,
            content="Fasad üçün smeta lazımdır, layihə mürəkkəbdir.",
        )
        Message.objects.create(
            conversation=c2,
            sender=MessageSender.AI,
            content="Fasad 120 AZN/m²-dən başlayır. Mürəkkəb layihə üçün menecerə ötürürəm.",
            label=MessageLabel.HUMAN_REQUIRED,
        )
        Message.objects.create(
            conversation=c2,
            sender=MessageSender.HUMAN,
            content="Salam Nigar xanım, smeta üçün planı WhatsApp-a göndərin.",
        )

        Lead.objects.create(
            business=abc,
            name="Elvin Quliyev",
            contact="+994 50 111 22 33",
            intent="150 m² ev tikintisi — Sumqayıt",
            source=LeadSource.INSTAGRAM,
            status=LeadStatus.NEW,
            conversation=c1,
        )
        Lead.objects.create(
            business=abc,
            name="Rəşad Əliyev",
            contact="+994 55 222 33 44",
            intent="Villa layihəsi",
            source=LeadSource.WEBSITE,
            status=LeadStatus.CONTACTED,
        )
        Lead.objects.create(
            business=abc,
            name="Leyla Məmmədova",
            contact="+994 70 333 44 55",
            intent="Təmir 90 m²",
            source=LeadSource.WHATSAPP,
            status=LeadStatus.QUALIFIED,
        )

        # Clinic
        clinic = businesses["dr-aysel-clinic"]
        cc = Conversation.objects.create(
            business=clinic,
            customer_name="Səbinə",
            channel="instagram",
            status=ConversationStatus.HUMAN,
            lead_potential=False,
        )
        Message.objects.create(
            conversation=cc,
            sender=MessageSender.CUSTOMER,
            content="Üzüm də səpgi var, hansı dərmanı içim?",
        )
        Message.objects.create(
            conversation=cc,
            sender=MessageSender.AI,
            content="Diaqnoz və dərman tövsiyəsi verə bilmirəm. Həkimə yönləndirirəm.",
            label=MessageLabel.HUMAN_REQUIRED,
        )
        Lead.objects.create(
            business=clinic,
            name="Kamilla Rəhimova",
            contact="+994 51 444 55 66",
            intent="Dermatoloji qəbul",
            source=LeadSource.INSTAGRAM,
            status=LeadStatus.NEW,
        )

        # Restaurant
        rest = businesses["urban-table"]
        rc = Conversation.objects.create(
            business=rest,
            customer_name="Orxan",
            channel="instagram",
            status=ConversationStatus.AI,
            lead_potential=True,
        )
        Message.objects.create(
            conversation=rc,
            sender=MessageSender.CUSTOMER,
            content="Şənbə axşamı 4 nəfərlik masa rezerv etmək istəyirəm.",
        )
        Message.objects.create(
            conversation=rc,
            sender=MessageSender.AI,
            content="Əlbəttə! Saat neçəyə rezerv edək?",
            label=MessageLabel.AI_ANSWERED,
        )
        Lead.objects.create(
            business=rest,
            name="Orxan Bayramov",
            contact="+994 50 777 88 99",
            intent="Şənbə rezervasiya — 4 nəfər",
            source=LeadSource.INSTAGRAM,
            status=LeadStatus.NEW,
            conversation=rc,
        )

        # Estate
        estate = businesses["prime-estate"]
        ec = Conversation.objects.create(
            business=estate,
            customer_name="Günel",
            channel="website",
            status=ConversationStatus.AI,
            lead_potential=True,
        )
        Message.objects.create(
            conversation=ec,
            sender=MessageSender.CUSTOMER,
            content="Nəsimidə 2 otaqlı kirayə axtarıram.",
        )
        Message.objects.create(
            conversation=ec,
            sender=MessageSender.AI,
            content="Nəsimidə 2 otaqlı variantlar 800–1400 AZN/ay aralığındadır. Büdcənizi deyin.",
            label=MessageLabel.AI_ANSWERED,
        )
        Lead.objects.create(
            business=estate,
            name="Günel Hüseynova",
            contact="+994 55 666 77 88",
            intent="2 otaq kirayə — Nəsimi",
            source=LeadSource.WEBSITE,
            status=LeadStatus.QUALIFIED,
            conversation=ec,
        )

    def _seed_analytics(self, businesses: dict[str, Business]):
        today = date.today()
        series_template = []
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            series_template.append({"date": d.isoformat(), "count": 12 + (i * 3) % 9})

        presets = {
            "abc-construction": {
                "messages_today": 48,
                "ai_answered": 39,
                "human_takeover": 6,
                "new_leads": 5,
                "response_rate": 0.96,
                "ai_vs_human": {"ai": 82, "human": 18},
                "lead_funnel": {"New": 5, "Contacted": 3, "Qualified": 2, "Converted": 1, "Lost": 1},
            },
            "dr-aysel-clinic": {
                "messages_today": 22,
                "ai_answered": 14,
                "human_takeover": 7,
                "new_leads": 2,
                "response_rate": 0.91,
                "ai_vs_human": {"ai": 65, "human": 35},
                "lead_funnel": {"New": 2, "Contacted": 2, "Qualified": 1, "Converted": 0, "Lost": 0},
            },
            "urban-table": {
                "messages_today": 35,
                "ai_answered": 30,
                "human_takeover": 3,
                "new_leads": 4,
                "response_rate": 0.94,
                "ai_vs_human": {"ai": 88, "human": 12},
                "lead_funnel": {"New": 4, "Contacted": 2, "Qualified": 2, "Converted": 1, "Lost": 0},
            },
            "prime-estate": {
                "messages_today": 28,
                "ai_answered": 23,
                "human_takeover": 4,
                "new_leads": 3,
                "response_rate": 0.93,
                "ai_vs_human": {"ai": 80, "human": 20},
                "lead_funnel": {"New": 3, "Contacted": 2, "Qualified": 2, "Converted": 1, "Lost": 1},
            },
        }
        for bid, biz in businesses.items():
            p = presets[bid]
            AnalyticsSnapshot.objects.create(
                business=biz,
                date=today,
                messages_today=p["messages_today"],
                ai_answered=p["ai_answered"],
                human_takeover=p["human_takeover"],
                new_leads=p["new_leads"],
                response_rate=p["response_rate"],
                messages_per_day=series_template,
                ai_vs_human=p["ai_vs_human"],
                lead_funnel=p["lead_funnel"],
            )
