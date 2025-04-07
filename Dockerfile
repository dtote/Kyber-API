# Usa una imagen base de Ubuntu
FROM ubuntu:20.04

# Establece la zona horaria (opcional)
ENV TZ=Europe/London
RUN apt-get update && apt-get install -y tzdata

# Instalar las dependencias necesarias
RUN apt-get update && apt-get install -y \
    g++ \
    cmake \
    libssl-dev \
    wget \
    libboost-all-dev

# Instalar OpenSSL 1.1 (en caso de que no esté presente)
RUN apt-get install -y openssl

# Copia el código fuente
COPY ./src /app
WORKDIR /app

# Compilar el proyecto
RUN make

# Copiar el binario a la imagen
#COPY ./mlKemAPIDil /usr/local/bin/mlKemAPIDil

# Exponer el puerto en el que la API escuchará
EXPOSE 5001

# Ejecutar el servidor
CMD ["/usr/local/bin/mlKemAPIDil"]
