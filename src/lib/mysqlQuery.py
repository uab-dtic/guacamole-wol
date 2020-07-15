#!/usr/bin/env python3

import mysql.connector

class mysqlQuery:
    db=0
    
    # 
    # init the connection
    #
    def __init__ ( self, hostname, database, user, password ):
        print ("mysqlQuery.__init__")

        self.db = mysql.connector.connect(
            host=hostname,
            database=database,
            user=user,
            passwd=password
            )

    #
    # Destroy the object
    #
    def __del__ ( self ):
        self.db.close()


    #
    # Do the query
    #
    def query ( self, sql ):
        #print ( "mysqlQuery.query : {}".format( sql ) )
        #print ( "mysqlQuery.query : connector {}".format( type (self.db) ) )

        mycursor = self.db.cursor()
        mycursor.execute( sql )

        myresult = mycursor.fetchall()

        self.db.commit()

        mycursor.close()

        #print ( "mysqlQuery.query: {}".format(myresult) )

        return myresult
