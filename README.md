# AI Köməkçi

Interactive multi-tenant SaaS demo: an Azerbaijani AI customer assistant for Instagram / WhatsApp / website.

AI answers from a Knowledge Base (mock RAG), detects leads, and shows a dashboard. UI language: **Azerbaijani (az)**.

## Quick start

```bash
python -m venv .venv

# Windows
.\.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env   # Windows
# cp .env.example .env   # macOS / Linux

python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Open http://127.0.0.1:8000/

- Login: `demo@aikomekci.az` (any password)
- Default tenant: `abc-construction`

## Architecture

```
config/          Django project settings + root URLs
core/            middleware, context processor, utils, JSON API
accounts/        fake demo login + onboarding
businesses/      tenants (Business) + seed_demo command
knowledge/       KnowledgeItem CRUD + keyword search service
conversations/   Conversation + Message inbox
leads/           Lead CRM-lite
ai/              AISettings + MockRAGResponder / OpenAI stub
channels/        Instagram / WhatsApp / Website connection status
analytics/       snapshots + dashboard KPIs / charts
demo/            Instagram-style live chat + scenario runner
marketing/       landing page
templates/       Django templates (AZ UI)
static/          CSS + demo.js
```

### Multi-tenancy

- Session key `current_business_id` (default `abc-construction`)
- `CurrentBusinessMiddleware` + `tenant` context processor
- Switching business filters dashboard/demo and clears demo conversation

### Mock AI pipeline (`ai/services/responder.py`)

1. Normalize Azerbaijani text (`ə→e`, `ı→i`, …)
2. Keyword search over `KnowledgeItem` (`knowledge/services/search.py`)
3. Detect intent (pricing, area, booking, medical_unsafe, …)
4. Business-type handlers (construction pricing by m², medical human handoff, …)
5. Lead detection: create Lead only when **AZ full name + +994 phone** appear
6. Return structured `AIResponse`

Greeting FAQs are down-ranked when the message is substantive (e.g. starts with “Salam” but asks about Xırdalan / m²).

## Plug in OpenAI later

1. Set in `.env`:

```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

2. Implement real logic in `OpenAIResponder` (`ai/services/responder.py`):
   - Embed knowledge chunks (replace keyword search in `knowledge/services/search.py`)
   - Chat completion with `AISettings.rules` as system prompt
   - Keep the same `AIResponse` interface so views/API stay unchanged

3. Optional future routes (commented in `config/urls.py` / `core/api.py`):
   - `POST /api/ai/chat/`
   - `POST /webhooks/whatsapp/`
   - `POST /webhooks/instagram/`

## Main routes

| Path | Purpose |
|------|---------|
| `/` | Landing |
| `/login/` | Demo login |
| `/onboarding/` | 5-step checklist |
| `/demo/` | Live Instagram-style chat |
| `/dashboard/` | KPIs |
| `/dashboard/conversations/` | Inbox |
| `/dashboard/knowledge/` | KB CRUD |
| `/dashboard/leads/` | Leads |
| `/dashboard/ai-settings/` | AI settings |
| `/dashboard/channels/` | Channels |
| `/dashboard/analytics/` | Charts |
| `POST /api/demo/chat/` | Demo AI endpoint |
| `POST /api/business/switch/` | Switch tenant |

## Real Instagram OAuth

Customers click **Instagram ilə daxil ol** — no passwords. Tokens are stored per business on `Channel`.

See **[docs/INSTAGRAM.md](docs/INSTAGRAM.md)**.

- Start OAuth: `/auth/instagram/`
- Callback: `/auth/instagram/callback/`
- Webhook: `/webhooks/instagram/`

Clear old demo tenants: `python manage.py clear_mock_data`

- Use PostgreSQL via `DATABASE_URL=postgres://...`
- Set `DEBUG=False`, strong `SECRET_KEY`, and `ALLOWED_HOSTS`
- `whitenoise` serves static files; run `collectstatic`
- This is a **demo**: no real Meta APIs, payments, or multi-user ACL

## License

Demo / educational use.
