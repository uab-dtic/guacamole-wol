#!/usr/bin/env python3

import os, sys

"""
obtiene las variables de entorno
"""
def get_env( listaVariables=[], exitIsError=False ):
    conjuntoVariables={}
    
    for VARIABLE in listaVariables:
        if VARIABLE in os.environ:
            conjuntoVariables[VARIABLE]=os.environ[VARIABLE]
        else:
            print ("NO {} defined.".format(VARIABLE) )
            if( exitIsError ):
                sys.exit()
    
    return conjuntoVariables
