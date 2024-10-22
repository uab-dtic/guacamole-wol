#!/usr/bin/env python3

import logging
import  paramiko
import  re

log = logging.getLogger( __name__ )

class sshCommand:
    connection=0
    hostName=""
    userName=""
    keyFileName=""
    keyPassPhrase=""
    

    #
    #
    #
    def __init__ ( self, host="", user="", key="", passphrase=""):
        self.hostName       = host
        self.userName       = user
        self.keyFileName    = key
        self.keyPassPhrase  = passphrase


    #
    #
    #
    def __del__ ( self ):
        self.hostName       = ""
        self.userName       = ""
        self.keyFileName    = ""
        self.keyPassPhrase  = ""

    #
    #
    #
    def launchCommand( self, command ):

        key = paramiko.RSAKey.from_private_key_file( self.keyFileName, self.keyPassPhrase )
        self.connection=paramiko.SSHClient()
        self.connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        log.debug ( "connecting to {}@{}".format(self.userName, self.hostName) )

        try:
            self.connection.connect( 
                    hostname        = self.hostName, 
                    username        = self.userName, 
                    pkey            = key 
                    )
        except Exception as e:
            log.critical( "SSH stdErr: '{}'".format (stderr.read() ))
            log.critical( "Error on ssh connection: '{}'".format(e))
            raise Exception ("SSH Connection error '{}'". format(e))
        else :
            log.debug ( "connected" )

            log.debug ( "Executing {}".format( command ) )
            stdin , stdout, stderr = self.connection.exec_command( command )

            resultado = stdout.read().decode("utf-8") # leo el resultado y lo transformo en string

            log.info( "SSH stdout: '{}'".format( resultado ))

            hostFound = re.search( "Found wakeonlan:", resultado, flags=re.IGNORECASE )
            if( not hostFound ):
                raise Exception( "host not found: '{}'".format( command ) )
            #
        finally:
            self.connection.close()

