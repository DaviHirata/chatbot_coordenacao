# Estágio 1: Build do app React
FROM node:18-alpine AS build

WORKDIR /app

COPY package.json ./
#COPY package-lock.json ./

RUN npm install

RUN npm install lucide-react

COPY . ./

RUN npm run build

# Estágio 2: Servir com Nginx
FROM nginx:stable-alpine

# Copiar os arquivos de build do estágio anterior
COPY --from=build /app/build /usr/share/nginx/html

# Copiar a configuração do Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
