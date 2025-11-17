# Estágio 1: Build da aplicação com Maven
FROM maven:3.9.6-eclipse-temurin-21-alpine AS build

WORKDIR /app

# Copiar o pom.xml e baixar as dependências
COPY pom.xml .
RUN mvn dependency:go-offline

# Copiar o código fonte e construir o JAR
COPY src ./src
RUN mvn clean install -DskipTests

# Estágio 2: Execução da aplicação
FROM eclipse-temurin:21-jdk-alpine

WORKDIR /app

# Copiar o JAR do estágio de build
COPY --from=build /app/target/*.jar app.jar

# Expor a porta do Spring Boot
EXPOSE 8080

# Comando para iniciar a aplicação
ENTRYPOINT ["java", "-jar", "app.jar"]
