# ---- Stage 1: build the React app with Node ----
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY . .
RUN npm run build

# ---- Stage 2: serve static files with unprivileged Nginx ----
# nginx-unprivileged runs as the non-root "nginx" user (uid 101) on port 8080.
FROM nginxinc/nginx-unprivileged:1.29-alpine
ENV BACKEND_URL=http://backend:8000
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
USER 101
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://127.0.0.1:8080/nginx-health || exit 1
