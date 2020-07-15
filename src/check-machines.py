#!/usr/bin/env python3

import os, sys, time

sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))
import get_environment as ge
import mysqlQuery as mq
import sshWOL as wol


CFG={}

#
# MAIN Code
#

def main():
    global CFG

    tiempoEspera = 10
    MaxWOL = 300 / tiempoEspera

    hostd={}
    oldDay=0

    sql = """
select 
    count(gh.username), gc.parameter_value as hostname
from
  guacamole_connection_history as gh, guacamole_connection_parameter gc
where
  `start_date`  > subtime( now(), sec_to_time (""" + str(tiempoEspera*4) + """ ) )
   and gh.connection_id=gc.connection_id
   and gc.parameter_name='hostname'
group by
   hostname;
    """


    query = mq.mysqlQuery( CFG['MYSQL_HOSTNAME'], CFG['MYSQL_DATABASE'], CFG['MYSQL_USER'], CFG['MYSQL_PASSWORD'] )

    sshCon = wol.sshCommand( CFG['WOL_SERVER'], CFG['WOL_USER'], CFG['WOL_KEY'], CFG['WOL_KEY_PASS'] )

    while ( True ):
        # reset hostDicytionary every day
        newDay=time.localtime().tm_mday
        if newDay != oldDay :
            hostd.clear()
            oldDay=newDay

        r = query.query ( sql )
        print ("main: {}".format(r))
        for row in r :
            cantidad = row[0]
            host = row[1]
            if cantidad >= 1 :
                if host in hostd :
                    hostd[host]+=1
                else:
                    hostd[host]=1

                if hostd[host] < MaxWOL :
                    sshCon.launchCommand( "WOL {}".format(host) )
                elif  hostd[host] == MaxWOL :
                    print ("Send mail WOL dont work {}".format(host))
                else:
                    print ("MaxWOL Supered on host {}".format(host))
            #
        # For All row
        time.sleep( tiempoEspera )
    # End while
    print ("endOfMainLoop");

#
#
#
if __name__ == "__main__" :

    CFG=ge.get_env( ['WOL_SERVER', 'WOL_USER', 'WOL_KEY', 'WOL_KEY_PASS', 'MYSQL_HOSTNAME', 'MYSQL_DATABASE', 'MYSQL_USER', 'MYSQL_PASSWORD' ] )
    #

    main ()
