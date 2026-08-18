# ---------- Build Stage ----------
FROM node:24-alpine AS build

WORKDIR /app

# Dependencies separat kopieren, damit Docker den Layer cachen kann
COPY package.json package-lock.json ./

RUN npm ci

# Angular Source kopieren
COPY . .

# Production Build
# Output-Pfad explizit setzen, damit der Docker-Build unabhängig
# von Angular-Defaults bleibt.
RUN npm run build -- --configuration production --output-path=dist/app


# ---------- Runtime Stage ----------
FROM nginx:alpine

# Eigene nginx-Konfiguration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Angular 21 application builder legt Browser-Dateien
# im Unterordner "browser" ab
COPY --from=build /app/dist/app/browser /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]