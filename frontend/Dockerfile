# IREN Analyzer frontend (Next.js). Build from the frontend/ directory:
#   docker build --build-arg NEXT_PUBLIC_BACKEND_URL=http://localhost:8000 -t iren-frontend frontend
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
# Public backend URL is baked into the browser bundle at build time (no secrets here).
ARG NEXT_PUBLIC_BACKEND_URL=""
ENV NEXT_PUBLIC_BACKEND_URL=$NEXT_PUBLIC_BACKEND_URL NEXT_TELEMETRY_DISABLED=1
RUN npm run build

FROM node:22-alpine
WORKDIR /app
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1 PORT=3000 HOSTNAME=0.0.0.0
COPY --from=build /app/.next/standalone ./
COPY --from=build /app/.next/static ./.next/static
COPY --from=build /app/public ./public
EXPOSE 3000
CMD ["node", "server.js"]
