#FROM python:3
FROM python:3.11-slim

LABEL MANTAINER Jordi.Roman@uab.cat
LABEL DESCRIPTION Check guacamole log on mysql table to launch a wol command if needed

RUN pip install --upgrade pip

# Creamos el usuario pythonuser con UID=GID=
ARG UID=1000
ARG GID=1000
ARG USER=pythonuser

RUN groupadd --gid ${GID} ${USER} ;                                              \
    useradd --gid ${GID} --uid ${UID} --shell /bin/false ${USER}

WORKDIR /app

COPY src/. .

# Creamos entorno virtual e instalamos dependencias
RUN python -m venv env  && \
    . env/bin/activate  && \
    pip install --upgrade pip   && \
    pip install --no-cache-dir -r requisitos.txt

# Cambiamos a usuario NO PRIVILEGIADO
USER ${USER}

# Variables de entorno necesarias 
ENV WOL_SERVER      dhcp-server
ENV WOL_USER        root
ENV WOL_KEY         /app/privateKeyComandosAulas
# Se debe montar un recurso para que esista este fichero
ENV WOL_KEY_PASS    PasswordSecretoDeLaPrivateKey

# Variables de funcionamiento
ENV PYTHONUNBUFFERED True

CMD . ./env/bin/activate && ./check-machines.py