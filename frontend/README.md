# IREN Analyzer: frontend

Next.js (App Router) + TypeScript + Tailwind + TradingView Lightweight Charts. It talks only to
the FastAPI backend (REST + WebSocket); API keys never reach the browser.

```bash
npm install
npm run dev        # http://localhost:3000 (backend must run on :8000)
npm run lint
npm run build
```

Set `NEXT_PUBLIC_BACKEND_URL` when the backend lives elsewhere (see `.env.example`).
