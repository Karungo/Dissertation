# Maasai Mara Wildlife Guide — PWA Frontend

A fully responsive Progressive Web App that works on:
- Desktop browsers (Chrome, Firefox, Safari, Edge)
- Mobile browsers (iOS Safari, Android Chrome)
- Installed as a home screen app on iOS and Android — no App Store needed

---

## What makes this a PWA

| Feature | Implementation |
|---|---|
| Installable | `manifest.json` + service worker |
| Offline support | `sw.js` caches static assets |
| Camera access | `<input capture="environment">` opens rear camera directly |
| Full screen | `"display": "standalone"` in manifest |
| Safe area | `env(safe-area-inset-*)` handles iPhone notch |
| iOS compatible | `apple-mobile-web-app-*` meta tags |
| Fast | nginx with proper cache headers |
| No App Store | Installed via browser "Add to Home Screen" |

---

## Files

```
pwa_frontend/
├── index.html      ← Full app (HTML + CSS + JS in one file)
├── manifest.json   ← PWA manifest
├── sw.js           ← Service worker (offline caching)
├── nginx.conf      ← nginx config with correct SW headers
├── Dockerfile      ← nginx:alpine container
├── icons/
│   ├── icon-192.png   ← Replace with your lion icon
│   └── icon-512.png   ← Replace with your lion icon
└── deploy_pwa.sh   ← Deploy to Cloud Run
```

---

## Step 1 — Set your API URL

Open `index.html` and update line:
```javascript
const API_URL = window.API_URL || "https://your-api-url.run.app";
```

Replace `https://your-api-url.run.app` with your Cloud Run API URL.

---

## Step 2 — Replace icons (optional but recommended)

Replace `icons/icon-192.png` and `icons/icon-512.png` with a
proper lion or Maasai Mara themed icon.
Any 192×192 and 512×512 PNG works.

---

## Step 3 — Deploy

```bash
export API_URL="https://your-api-url.run.app"
./deploy_pwa.sh
```

---

## Step 4 — Install on phone (no App Store)

### Android (Chrome)
1. Visit your Cloud Run URL in Chrome
2. Tap the three-dot menu → "Add to Home screen"
3. Tap "Install"
4. App appears on home screen like a native app

### iPhone (Safari)
1. Visit your Cloud Run URL in Safari
2. Tap the Share button (box with arrow)
3. Tap "Add to Home Screen"
4. Tap "Add"
5. App appears on home screen — opens full screen with no browser UI

---

## How camera works on mobile

```html
<!-- Opens rear camera directly on mobile -->
<input type="file" accept="image/*" capture="environment">

<!-- Opens front camera -->
<input type="file" accept="image/*" capture="user">

<!-- Opens file picker / gallery -->
<input type="file" accept="image/*">
```

The app provides both "Take Photo" (rear camera) and
"Choose Photo" (gallery) buttons so tourists can use either.

---

## Updating the app

```bash
# After any code change
docker build -t gcr.io/dissertation-498512/maasai-mara-pwa .
docker push gcr.io/dissertation-498512/maasai-mara-pwa
gcloud run deploy maasai-mara-pwa \
  --image gcr.io/dissertation-498512/maasai-mara-pwa \
  --region europe-west2
```
