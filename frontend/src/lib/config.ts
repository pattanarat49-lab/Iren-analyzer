// Backend base URL. The browser only ever talks to our own FastAPI backend; API keys stay there.
// Set NEXT_PUBLIC_BACKEND_URL at build time for deployments (e.g. https://iren-api.example.com).
// Locally it defaults to port 8000 on the same host the page was loaded from.
export function backendUrl(): string {
  const configured = process.env.NEXT_PUBLIC_BACKEND_URL;
  if (configured) return configured.replace(/\/$/, "");
  if (typeof window === "undefined") return "http://localhost:8000";
  return `${window.location.protocol}//${window.location.hostname}:8000`;
}

export function wsUrl(): string {
  return backendUrl().replace(/^http/, "ws") + "/ws";
}
