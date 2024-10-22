#!/usr/bin/env python3

import os, sys
import logging
import datetime, time

# Obtiene las variables de entorno
import get_environment as ge

# Clase para realizar las peticiones via SSH
import sshWOL as wol

# Librerias de gestion de bbdd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Librerias para el cliente de prometheus
from prometheus_client import start_http_server, Summary, Counter, Gauge

CFG={}


# Función para crear un motor de base de datos
def create_db_engine(db_type, user, password, host, port, db_name):
    if db_type == 'postgres':
        # PostgreSQL
        url = f'postgresql://{user}:{password}@{host}:{port}/{db_name}'
    elif db_type == 'mysql':
        # MySQL/MariaDB con mysql-connector-python
        url = f'mysql+mysqlconnector://{user}:{password}@{host}:{port}/{db_name}'
    elif db_type == 'mariadb':
        # MariaDB con PyMySQL
        url = f'mariadb+pymysql://{user}:{password}@{host}:{port}/{db_name}'
    else:
        raise ValueError('Base de datos no soportada')

    # Crear el motor de la base de datos
    engine = create_engine(url)
    return engine

#
# MAIN Function
#

def main():
    global CFG

    tiempoEspera = 15   # >= Tiempo de espera de la reconexion de guacamole


    MaxWOL = 300 / tiempoEspera

    # diccionario de maquinas a hostd[maquina]=numeroWoLEjecutados
    hostd={}

    # Ultimo dia de ejecucion
    oldDay=0

    sql = 'select count(gh.username), gc.parameter_value as hostname '
    sql += 'from guacamole_connection_history as gh, guacamole_connection_parameter gc '
    sql += 'where '
    sql += '`start_date` > subtime( now(), sec_to_time (" ' + str(tiempoEspera*4) + '" ) ) '
    sql += 'and gh.connection_id=gc.connection_id '
    sql += 'and gc.parameter_name="hostname" '
    sql += 'group by hostname;'

    log.debug( "SQL: '{}'".format(sql))
   
    # Crear el motor de base de datos
    engine = create_db_engine( CFG['DB_TYPE'], CFG['DB_USER'], CFG['DB_PASSWORD'], CFG['DB_HOSTNAME'], CFG['DB_PORT'], CFG['DB_DATABASE'], )
    log.debug( "Engine : '{}'".format(engine))

    # Crear una sesión para interactuar con la base de datos
    Session = sessionmaker(bind=engine)
    
    sshCon = wol.sshCommand( CFG['WOL_SERVER'], CFG['WOL_USER'], CFG['WOL_KEY'], CFG['WOL_KEY_PASS'] )
    log.debug( "sshCon: '{}'".format(sshCon))

    while ( True ):

        with execution_time.time():     # Medir el tiempo de ejecucion de cada iteracion

            # reset hostDicytionary every day
            newDay=time.localtime().tm_mday
            if newDay != oldDay :
                log.info( "Clean hostd by newDay ({}vs{}): '{}'".format(oldDay, newDay, hostd))
                hostd.clear()
                oldDay=newDay
            #

            try :
                # Iniciamos sesion para cada iteracion
                session = Session()
                log.debug( "session: '{}'".format(session))
                # Ejecutar La query
                r = session.execute( text( sql ) ).fetchall()
            except SQLAlchemyError as err:
                db_connections_failure.inc()
                log.critical ("Database Error: '{}'".format( err ))
            except Exception as e:
                log.critical("Error inesperado '{}'".format(e))
            #
            else:
                db_connections_success.inc()
                db_connections_failure.set(0)

                log.debug ("Solicitudes WOL Historicas : '{}'".format(hostd))
                log.debug ("Solicitudes WOL Nuevas     : '{}'".format(r))

                wolNuevas={} # Diccionario temporal para hacer limpieza de las historicas
                for row in r :
                    cantidad = row[0]   # Numero de usuarios solicitando el WOL
                    host = row[1]       # Maquina de la se solicita el wol
                    wolNuevas[host]=cantidad
                    if cantidad >= 1 :
                        if host in hostd :
                            hostd[host]+=1
                        else:
                            hostd[host]=1
                        if hostd[host] < MaxWOL :
                            log.info( "Sending SSH WOL: 'WOL {}'".format(host))
                            try :
                                sshCon.launchCommand( "WOL {}".format(host) )
                            except Exception as e:
                                log.critical( "Error al realizar la conexion SSH : '{}'".format(e))
                                ssh_connections_failure.inc()
                            else:
                                ssh_connections_success.inc()
                                ssh_connections_failure.set(0)  # Reseteamos el contador de errores al hacer una conexion valida
                            #
                        else:
                            log.critical ("MaxWOL Supered on host {}".format(host))
                            log.critical ("Send mail 'WOL dont work on {}'".format(host))
                            # reinicializamos contador de WOL
                            hostd[host] = MaxWOL
                    #
                    log.info( "hostd : '{}'".format(hostd))
                # For All row
                wol_requests.inc( len (wolNuevas)) # Añadimos las nuevas solicitudes de Wol
            
                # Hacemos limpieza de 
                for maquina in hostd.copy() :
                    # Eliminamos de la lista de maquinas con solicitudes de conexion, la maquina que no ha recibido una solicitud 
                    if maquina not in wolNuevas: 
                        log.debug( "Purgamos la maquina '{}' de la lista de maquinas con solicitudes de conexion". format(maquina))
                        del(hostd[maquina])
                    #
                #
            finally:
                # Cerramos la sesion de bbdd 
                session.close()
            #
        # Medir execution_time del ciclo

        log.debug( "Sleeping: {} seconds".format(tiempoEspera))
        time.sleep( tiempoEspera )
        log.info( "Ahora = {}". format( datetime.datetime.now() ))

        # Registrar el tiempo total de ejecución
        total_execution_time.observe(time.time() - start_time)

    # End while
    log.critical ("endOfMainLoop")
#


#
#
#
if __name__ == "__main__" :

    # Obtiene las variables de entorno para la configuracion
    CFG=ge.get_env( ['WOL_SERVER', 'WOL_USER', 'WOL_KEY', 'WOL_KEY_PASS', 'DB_TYPE', 'DB_HOSTNAME', 'DB_PORT', 'DB_DATABASE', 'DB_USER', 'DB_PASSWORD' ] )
    #
    # Captura el valor de la variable de entorno LOGLEVEL, sino está instanciada por defecto vale 'WARNING'
    LOGLEVEL = os.environ.get('LOGLEVEL','INFO')
    # Set loglevel by default
    logging.basicConfig( stream=sys.stdout, level=LOGLEVEL ) 

    # Set loglevel for paramiko's module to warning
    logging.getLogger("paramiko").setLevel(logging.WARNING)
    logging.getLogger("sshWOL").setLevel(logging.INFO)
    
    log = logging.getLogger( __name__ )

    log.debug ( "CFG: {}".format(CFG))

    # Set loglevel for paramiko's module to warning
    logging.getLogger("paramiko").setLevel(logging.WARNING)
    logging.getLogger("sshWOL").setLevel(logging.INFO)
    
    log = logging.getLogger( __name__ )

    log.debug ( "CFG: {}".format(CFG))

    # Definir las metricas de prometheus
    db_connections_success = Gauge('db_connections_success_total', 'Número de conexiones a BBDD satisfactorias')
    db_connections_failure = Gauge('db_connections_failure_total', 'Número de conexiones a BBDD fallidas')

    ssh_connections_success = Gauge('ssh_connections_success_total', 'Número de conexiones SSH satisfactorias')
    ssh_connections_failure = Gauge('ssh_connections_failure_total', 'Número de conexiones SSH fallidas')

    execution_time = Summary('execution_time_seconds', 'Tiempo de ejecución de cada iteración')
    wol_requests = Counter('wol_requests', 'Número de peticiones de Wake On Lan')

    total_execution_time = Summary('total_execution_time_seconds', 'Tiempo total de ejecución del proceso')

    # Empezar el servidor HTTP en un puerto específico para que Prometheus recoja las métricas
    start_http_server(8000)

    start_time = time.time()    # Para el tiempo total de ejecucion

    # Proceso principal
    main ()
