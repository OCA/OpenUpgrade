#!/usr/bin/python
import etl
xmlrpc_conn=etl.connector.xmlrpc_connector('localhost',5000)

xmlrpc_in= etl.component.input.xmlrpc_in(xmlrpc_conn)

log1=etl.component.transform.logger(name='File11')

tran=etl.transition(xmlrpc_in,log1)
job2=etl.job([log1])

job2.run()