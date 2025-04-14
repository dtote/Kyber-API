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
    libboost-all-dev \
    git \
    build-essential

# Instalar OpenSSL 1.1 (en caso de que no esté presente)
RUN apt-get install -y openssl

# Establecer las variables de entorno a partir del archivo .env
RUN git clone https://$GITHUB_TOKEN@github.com/open-quantum-safe/liboqs.git /app/liboqs

# Construir liboqs usando los comandos básicos
WORKDIR /app/liboqs
RUN git submodule update --init --recursive
RUN mkdir build && cd build && cmake .. && make && make install

# Copiar el código fuente de tu proyecto
COPY . /app
WORKDIR /app

# Run 
RUN make

# Exponer el puerto en el que la API escuchará
EXPOSE 5001

# Ejecutar el ejecutable desde /app/mlKemAPIDil
CMD ["/app/mlKemAPIDil"]
