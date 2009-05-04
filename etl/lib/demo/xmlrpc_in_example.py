#!/usr/bin/python
import etl

sort1=etl.component.transform.sort('name')
log1=etl.component.transform.logger(name='After Sort')
tran1=etl.transition(sort1, log1)
job1=etl.job([sort1,log1])
xmlrpc_conn=etl.connector.xmlrpc_connector('localhost',5000)
xmlrpc_in= etl.component.input.xmlrpc_in(xmlrpc_conn, job1)
job2=etl.job([xmlrpc_in])
job2.run()
