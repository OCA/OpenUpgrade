# -*- encoding: utf-8 -*-
##############################################################################
#
#    ETL system- Extract Transfer Load system
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

"""
To provide connectivity with sql database server. 
supported connection with :
postgres server
mysql server
oracle server
"""
from etl.connector import connector
class sql_connector(connector):    
    def __init__(self, host,port, db, uid, passwd,sslmode='allow',con_type='postgres'):
        super(sql_connector, self).__init__()
        self.uri = host+':'+str(port)
        self.host=host
        self.port=port
        self.sslmode=sslmode             
        self.db = db
        self.uid = uid
        self.con_type = con_type
        self.passwd = passwd         
        
         
    def open(self):
        super(sql_connector, self).open()
        connector=False
        if self.con_type=='postgres':
            import psycopg2
            connector = psycopg2.connect("dbname=%s user=%s host=%s port=%s password=%s sslmode=%s" \
                                % (self.db,self.uid,self.host,self.port,self.passwd,self.sslmode))
        elif self.con_type=='mysql':
            import MySQLdb
            connector = MySQLdb.Connection(db=self.db, host=self.host,port=self.port, user=self.uid,passwd=self.pwd)
        elif self.con_type=='oracle':
            import cx_Oracle
            dsn_tns = cx_Oracle.makedsn(self.host, self.port, self.db)
            connector = cx_Oracle.connect(self.uid, self.passwd, dsn_tns)    
        else:
            raise Exception('Not Supported')           
        return connector    

    def close(self,connector):  
        super(sql_connector, self).close()          
        return connector.close()

    def __copy__(self): 
        res=sql_connector(self.host,self.port, self.db, self.uid, self.passwd,self.sslmode,self.con_type)        
        return res

def test():    
    #TODO
    pass

if __name__ == '__main__':
    test()

