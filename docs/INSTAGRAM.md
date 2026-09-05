# Real Instagram OAuth + Messaging (AI Assistant)

## Customer flow (no passwords)

1. User clicks **Instagram ilə daxil ol**
2. Meta / Instagram OAuth consent (`instagram_business_basic`, `instagram_business_manage_messages`)
3. Callback creates/updates `Business` + `Channel` with access token
4. Incoming DMs hit `POST /webhooks/instagram/` → AI → reply with that account’s token

## Meta App setup

1. [developers.facebook.com](https://developers.facebook.com) → your app
2. Add **Instagram** product → **API setup with Instagram Login** / Business Login
3. Add OAuth redirect URI (must match exactly):

   `{PUBLIC_BASE_URL}/auth/instagram/callback/`

   Example: `https://xxxx.trycloudflare.com/auth/instagram/callback/`

4. Webhooks callback: `{PUBLIC_BASE_URL}/webhooks/instagram/`  
   Verify token: `META_VERIFY_TOKEN` (default `aikomekci_verify`)  
   Subscribe: **messages**
5. Put App ID / Secret in `.env` as `META_APP_ID` / `META_APP_SECRET`  
   (and `INSTAGRAM_APP_ID` / `INSTAGRAM_APP_SECRET` if Meta shows separate Instagram credentials)

## Local HTTPS

```bash
python manage.py runserver 0.0.0.0:8000
cloudflared tunnel --url http://127.0.0.1:8000
```

Set `PUBLIC_BASE_URL` and `INSTAGRAM_REDIRECT_URI` to the tunnel HTTPS URL, add host to `ALLOWED_HOSTS`, restart Django.

## Clear old mock tenants

```bash
python manage.py clear_mock_data
```

## App Review

Development mode: only app roles / testers can complete OAuth.  
For any Instagram business customer: submit App Review for messaging permissions and switch app to Live.
