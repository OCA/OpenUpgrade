##!/usr/bin/python
#import sys
#sys.path.append('..')
#

#
#ooconnector = etl.connector.openobject_connector('http://localhost:8069', 'etl', 'admin', 'admin', con_type='xmlrpc')
#
#map = etl.component.transform.map({'main':{
#    'id': "tools.uniq_id(main.get('org', 'anonymous'), prefix='partner_')",
#    'address_id': "tools.uniq_id(main.get('fn', 'anonymous'), prefix='contact_')",
#    'name': "main.get('org',['anonymous'])[0]",
#    'contact_name': "main.get('fn','anonymous')",
#    'email': "main.get('email','').upper()"
#}})
#
#oo_out= etl.component.output.openobject_out(
#     ooconnector,
#     'res.partner',
#     {'id':'id','name':'name'}
#)
#
#oo_out2= etl.component.output.openobject_out(
#     ooconnector,
#     'res.partner.address',
#     {'name': 'contact_name', 'id':'address_id', 'partner_id:id':'id','email':'email'}
#)
#log1=etl.component.transform.logger(name='vCard->Oo')
#
#
#tran=etl.transition(map,log1)
#tran=etl.transition(log1,oo_out)
#tran=etl.transition(oo_out,oo_out2)
#
#log2=etl.component.transform.logger(name='Count')
#
#count = etl.component.control.data_count()
#tran=etl.transition(map, count, channel_destination='gmail')
#tran=etl.transition(oo_out, count, channel_destination='partner')
#tran=etl.transition(oo_out2, count, channel_destination='address')
#tran=etl.transition(count, log2)
#
#
#job1=etl.job([oo_out2, log2],'Sub job')
#
#xmlrpc_conn=etl.connector.xmlrpc_connector('localhost',5000)
#xmlrpc_conn.start('import_data')
##xmlrpc_in= etl.component.input.xmlrpc_in(job1)
##xmlrpc_conn.start('import_data')
#xmlrpc_in= etl.component.input.xmlrpc_in(xmlrpc_conn)
#xmlrpc_out= etl.component.output.xmlrpc_out(xmlrpc_conn)
#
#tran=etl.transition(log1,map)
#tran=etl.transition(map,xmlrpc_in)#,map
#j2=etl.job([xmlrpc_in])
#j2.run()
#
#tran=etl.transition(map,xmlrpc_out)
#j2=etl.job([xmlrpc_out])
#j2.run()
##tran=etl.transition(xmlrpc_in,xmlrpc_out)
#job2=etl.job([xmlrpc_out])
#job2.run()
#
#
##two job run

#!/usr/bin/python
#import sys
import etl


ooconnector = etl.connector.openobject_connector('http://mra.tinyerp.co.in:8069', 'etl', 'admin', 'admin', con_type='xmlrpc')
oo_out_partner= etl.component.output.openobject_out(
     ooconnector,
     'res.partner',
     {'id':'id','name':'name'}
            )

xmlrpc_conn=etl.connector.xmlrpc_connector('localhost',5000)

xmlrpc_in= etl.component.input.xmlrpc_in(xmlrpc_conn)
log2=etl.component.transform.logger(name='Partner File')
tran=etl.transition(log2,xmlrpc_in)
tran=etl.transition(xmlrpc_in,oo_out_partner)
#tran=etl.transition(xmlrpc_in,)
job2=etl.job([oo_out_partner])



fileconnector_partner=etl.connector.localfile('input/partner.csv')
csv_in1= etl.component.input.csv_in(fileconnector_partner,name='Partner Data')
log1=etl.component.transform.logger(name='Read Partner File')
xmlrpc_out = etl.component.output.xmlrpc_out(xmlrpc_conn)

tran=etl.transition(csv_in1,log1)
tran=etl.transition(log1,xmlrpc_out)

job1=etl.job([xmlrpc_out])
job1.run()

job2.run()









