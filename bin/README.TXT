La clave publica se genera con el comando

# ssh-keygen -b 4096 -C "Comandos Remotos Sobre Aulas" -f comandosAulas

Añadir al principio de la clave publica el nombre del comando que podrá ejecutar

 $ cat comandosAulas.pub
 command="/usr/local/sbin/comandosAulas.sh" ssh-rsa AAAAB.....

Añadir la clave publica al authorized_keys del usuario (root?) del servidor de dhcp

Dependencias:
- iproute2
- etherwake
- perl
