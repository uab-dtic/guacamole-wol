La clave publica generada

# ssh-keygen -b 4096 -C "Comandos Remotos Sobre Aulas"

Añadir al authorized_keys debe tener el siguiente prefijo para que funcione

command="/usr/local/sbin/comandosAulas.sh" ssh-rsa AAAAB.....
