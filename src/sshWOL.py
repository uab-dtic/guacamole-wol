#!/usr/bin/env python3

import logging

import  paramiko

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

        self.connection.connect( 
                hostname        = self.hostName, 
                username        = self.userName, 
                pkey            = key 
                )
        log.debug ( "connected" )

        log.debug ( "Executing {}".format( command ) )
        stdin , stdout, stderr = self.connection.exec_command( command )
        log.info( "SSH stdout: '{}'".format( stdout.read() ))
        log.debug( "SSH stdErr: '{}'".format (stderr.read() ))
        
        self.connection.close()

