# ── Stage 1: Build ───────────────────────────────────────────────────────────
FROM node:20-alpine AS builder
WORKDIR /app

RUN corepack enable && corepack prepare pnpm@9.15.0 --activate

# Copy workspace manifests first for layer caching
COPY package.json pnpm-workspace.yaml ./
# pnpm-lock.yaml may not exist on first build — copy only if present
COPY pnpm-lock.yaml* ./

# Copy workspace package manifests (needed for install to resolve workspace deps)
COPY apps/web/package.json ./apps/web/
COPY packages/ ./packages/

RUN pnpm install --no-frozen-lockfile --ignore-scripts

# Copy app source
COPY apps/web/ ./apps/web/

ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL

RUN pnpm --filter @yua/web build

# ── Stage 2: Serve ────────────────────────────────────────────────────────────
FROM nginx:1.27-alpine

COPY --from=builder /app/apps/web/dist /usr/share/nginx/html
COPY apps/web/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
