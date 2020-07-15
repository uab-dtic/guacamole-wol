FROM python:3

LABEL MANTAINER Jordi.Roman@uab.cat
LABEL DESCRIPTION Check guacamole log on mysql table to launch a wol command if needed

WORKDIR /usr/src/app

COPY src/requisitos.txt ./

RUN pip install --no-cache-dir -r requisitos.txt

COPY src/. .

#ENV WOL_SERVER 
#ENV WOL_USER 
#ENV WOL_KEY 
ENV PYTHONUNBUFFERED True

CMD [ "python", "./check-machines.py" ]
