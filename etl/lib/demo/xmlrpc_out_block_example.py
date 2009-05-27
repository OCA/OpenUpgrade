#!/usr/bin/python
import etl

xmlrpc_conn=etl.connector.xmlrpc_connector('localhost',5000)

xmlrpc_out = etl.component.output.xmlrpc_out_block(xmlrpc_conn)
filevcard = etl.connector.localfile('input/contacts.vcf')
vcard_in1 = etl.component.input.vcard_in(filevcard)
map = etl.component.transform.map({'main':{    
    'org': "main.get('org',['anonymous'])[0]",
    'fn': "main.get('fn','anonymous')",
    'email': "main.get('email','')"
}})
log2=etl.component.transform.logger(name='File')

tran=etl.transition(vcard_in1,map)
tran=etl.transition(map,xmlrpc_out)
tran=etl.transition(xmlrpc_out,log2)
job1=etl.job([vcard_in1,map,xmlrpc_out,log2])

job1.run()
