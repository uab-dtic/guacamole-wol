# Imagen guacamole-wol

Esta imagen contiene un script que con un usuario no privilegiado (uid=1000) se conecta a la bbdd de guacamole para buscar los intentos de conexion por parte de un usuario a una maquina en concreto.
Cuando hay intentos de conexiones que no se solucionan, se lanza una conexión ssh :

- contra *WOL_USER@WOL_SERVER*
- usando la key *WOL_KEY* y el password *WOL_KEY_PASS*
- con el comando 'WOL NombreConexion'

El *WOL_SERVER* debe estar configurado con los scripts del directorio *bin* y el usuario *WOL_USER* debe estar configurado de forma que permita la conexión ssh con la key *WOL_KEY* y que solo pueda ejecutar el comando  *comandos_aulas.sh* que a su vez llamará al script *my_wakeonlan*

## Instalacion en el WOL_SERVER

Los elementos para hacer la instalacion en el servidor de WOL son:

- Copiar los scripts del directorio bin al directorio /usr/local/bin
- Instalar el paquete etherwake
- instalar la pub_key en el ~${WOL_USER}/.ssh/authorized_keys de forma que se ejecute solo el script *comandos_aulas.sh*

```data
command="/usr/local/bin/comandos_aulas.sh" ssh-rsa AAAAB3Nz.....VyQ== Comandos Remotos Sobre Aulas
```

## Variables de entorno y volumenes

- WOL_SERVER    FQDN o IP del servidor que realizará el WOL (debe tener el fichero de dhcp)
- WOL_USER      Usuario del WOL_SERVER que ejecutará el comando
- WOL_KEY       Ruta de la ssh private key, dentro del contenedor (Ver el Volumen)
- WOL_KEY_PASS  Password para poder usar la ssh private key
- DB_TYPE       Tipo de servidor de bbdd (mysql, postgres, mariadb, etc.)
- DB_HOSTNAME   Servidor de bbdd
- DB_PORT       Puerto de la bbdd
- DB_DATABASE   Nombre de la bbdd
- DB_USER       Usuario de acceso a la bbdd
- DB_PASSWORD   Password del usuario de bbdd

Respecto a la ssh private key es necesario :

- Montar un volumen con el fichero de la ssh private key y que la variable *WOL_KEY* apunte correctamente al fichero.
- El fichero original ha de pertenecer al UID=1000 GID=1000 y tener los permisos 0600

## NOTAS

## TASQ-10152

Ante un cambio de bbdd de mysql por mariadb que deberia ser tranparente, nos hemos dado cuenta de que el codigo NO FUNCIONABA con la nueva bbdd. Ante este problema hemos decidido refactorizar el codigo para que el motor de bbdd sea independiente del codigo a usar.
