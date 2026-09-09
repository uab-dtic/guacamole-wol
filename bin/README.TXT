## Documentacion ssh

La clave publica se genera con el comando

# ssh-keygen -b 4096 -C "Comandos Remotos Sobre Aulas" -f comandosAulas

Añadir al principio de la clave publica el nombre del comando que podrá ejecutar

 $ cat comandosAulas.pub
 command="/usr/local/bin/comandosAulas.sh" ssh-rsa AAAAB.....

Añadir la clave publica al authorized_keys del usuario (root?) del servidor de dhcp


## Dependencias de paquetes
- iproute2
- etherwake
- jq, node-json5
- isc-dhcp | kea

## Instalacion y Configuracion local

- Copiar el contenido de la carpeta bin a /usr/local/bin
- Añadir la ssh pub key de guacamole al usuario root (obtener del servidor de guacamole)
- Modificar el script /usr/local/bin/my_wakeonlan
    - configure la variable *DHCP_SERVER* al valor que corresponda
- Comprobar el funcionamiento del script ejecutandolo: 
``` bash
/usr/local/bin/my_wakeonlan sab-b01
```
    - Asegurar la existencia de el/los ficheros necesarios
    - Asegurar la existencia de los binarios necesarios

## Configuracion del servidor remoto guacamole-wol

- Probar la conexion desde el servidor de guacamole
``` bash

. ./docker-compose.wol.variables

ssh -i comandosAulas -o StrictHostKeyChecking=no,UserKnownHostsFile=/dev/null ${WOL_USER}@${WOL_SERVER} WOL <NOMBRE_DE_MAQUINA>
Warning: Permanently added '<WOL_SERVER>' (ED25519) to the list of known hosts.
Enter passphrase for key 'comandosAulas': 
WOL sab-b01
Found wakeonlan: <NOMBRE_DE_MAQUINA>: <IP> - <MAC ADDRESS> . -

```

- Configurar el servidor en el daemon guacamole-wol 
    - docker-compose.wol.variables
- Reiniciar contenedor ( docker compose up -d )

- Comprobar el funcionamiento desde el servidor de guacamole en real
    