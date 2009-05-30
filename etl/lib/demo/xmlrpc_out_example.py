#!/usr/bin/python
import etl

xmlrpc_conn=etl.connector.xmlrpc_connector('localhost',5000)

xmlrpc_out = etl.component.output.xmlrpc_out(xmlrpc_conn)
fileconnector_partner=etl.connector.localfile('input/partner.csv')
csv_in1= etl.component.input.csv_in(fileconnector_partner,name='Partner Data')

log2=etl.component.transform.logger(name='File')

tran=etl.transition(csv_in1,xmlrpc_out)
tran=etl.transition(xmlrpc_out,log2)
job1=etl.job([log2])

job1.run()
