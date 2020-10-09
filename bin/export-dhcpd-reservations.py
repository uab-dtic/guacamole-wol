#!/usr/bin/env python3

import re, sys, getopt, socket

name="dhcpd.sbd.conf"

#
#  Mensajes de ayuda
#
def help( error = 0):
    print( "DHCP 2 CSV converter")
    print( "Forma de uso:")
    print( "    {} -i ficheroDHCP -o ficheroCSV".format( __file__ ) )
    sys.exit( error )

#
#  Funcion principal
#
def main ( argv ):

    dhcpFile =""
    csvFile  = ""


    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        help( 2 )
      
    for opt, arg in opts:
        if opt == '-h':
            help()
         
        elif opt in ("-i" ):
            dhcpFile = arg
        elif opt in ("-o"):
            csvFile = arg

    # Lee el fichero de dhcp
    try :
        f = open( dhcpFile, "r")
        c = f.read()
        f.close()
    except :
        print ( "Error accediendo al fichero de dhcp: '{}'".format( dhcpFile ))

    # manipula el contenido de los datos
    c = c.lower()                           # a minusculas
    c = re.sub( "#.*[\n\r]", "", c)         # Elimina comentarios
    c = re.sub ( "\t", " ", c)              # elimina tabuladores
    c = re.sub ( " {2,}", " ", c)           # multiples espacios
    c = c.replace( "\n", " ").replace("host ","\nhost ")    # cada 'host ' a una linea nueva 

    # Busca todos los registros 'host '
    x = re.findall( "host .*", c )

    csvContent = ""
    a=0
    for ii in x :
        a += 1
        ii = re.sub( "}.*","}", ii )    # elimino el tailing de otros objetos
        ii = re.sub( " {2,}"," ", ii )
        p = re.compile(" *[{;}] *")
        elements = p.split(ii)
        # Debug
        #print ( " {} - {} - {} ".format (a, ii, elements) )
        # Temp Vars
        dhcpName  = ""
        dhcpEther = ""
        dhcpIP    = ""
        dhcpFQDN  = ""
        for e in elements:
        
            if ( "host " in e ):
                dhcpName = e.split(" ")[1]
            elif ( "fixed-address " in e ):
                dhcpIP = e.split(" ")[1]
                dhcpFQDN = socket.getfqdn(dhcpIP)

            elif ( "hardware ethernet " in e ):
                dhcpEther = e.split( " ")[2]
            #

        #
        csvContent += "{};{};{};{};\n".format( dhcpName, dhcpEther, dhcpIP, dhcpFQDN)
    # end process records

     # Escribe el fichero de csv
    try :
        f = open( csvFile, "w")
        c = f.write( csvContent)
        f.close()
    except :
       print ( "Error generando el fichero de csv: '{}'".format( dhcpFile ))
    #
#

        
#
# Proceso principal
#
if __name__ == "__main__":
    if( len( sys.argv ) < 4) :
        help( 2 )
    #
    main(sys.argv[1:])