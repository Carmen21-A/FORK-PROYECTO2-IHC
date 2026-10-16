# syntax=docker/dockerfile:1

# ---------- Etapa 1: compilar Flutter Web ----------
FROM ghcr.io/cirruslabs/flutter:stable AS build

WORKDIR /app

# Copiamos primero los manifiestos para aprovechar la cache de dependencias
COPY pubspec.yaml pubspec.lock ./
RUN flutter pub get

# Copiamos el resto del proyecto y compilamos en modo release
COPY . .
RUN flutter build web --release

# ---------- Etapa 2: servir con nginx ----------
FROM nginx:alpine

# Configuracion propia de nginx (SPA + cache de assets)
COPY nginx/default.conf /etc/nginx/conf.d/default.conf

# Artefactos compilados por Flutter
COPY --from=build /app/build/web /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
