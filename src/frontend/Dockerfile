FROM node:20-alpine AS build

WORKDIR /app

ARG VITE_BASE_PATH=/
ENV VITE_BASE_PATH=$VITE_BASE_PATH

COPY package*.json ./
RUN npm install
RUN npm ci

COPY . .
RUN npm run build

FROM node:20-alpine AS runtime

WORKDIR /app

COPY --from=build /app/dist ./dist
COPY server.js ./server.js

EXPOSE 3000

CMD ["node", "server.js"]
