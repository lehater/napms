FROM node:22-alpine AS build

WORKDIR /app/web

COPY web/package.json web/package-lock.json ./
RUN npm ci --no-audit --no-fund

COPY web/index.html web/tsconfig.json web/vite.config.ts web/components.json ./
COPY web/scripts ./scripts
COPY web/src ./src
COPY docs/contracts/ui/mvp-design-tokens.json /app/docs/contracts/ui/mvp-design-tokens.json

RUN npm run build

FROM nginx:1.27-alpine AS runtime

COPY web/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/web/dist /usr/share/nginx/html

EXPOSE 8080

HEALTHCHECK --interval=5s --timeout=3s --retries=12 \
  CMD wget -qO- http://127.0.0.1:8080/health/live >/dev/null || exit 1
