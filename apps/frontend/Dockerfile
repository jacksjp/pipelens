# syntax=docker/dockerfile:1.7
# Multi-stage: build the React app, then serve the static bundle with nginx.

ARG NODE_VERSION=20
FROM node:${NODE_VERSION}-alpine AS build
WORKDIR /app

COPY apps/frontend/package.json apps/frontend/package-lock.json* ./
RUN npm ci || npm install

COPY apps/frontend/ .
RUN npm run build

FROM nginx:1.27-alpine AS runtime
COPY --from=build /app/dist /usr/share/nginx/html
COPY apps/frontend/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
