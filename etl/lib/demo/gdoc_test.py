#!/usr/bin/python
import threading
import sys
sys.path.append('..')

import etl



gdoc_connector = etl.connector.gdoc_connector(user,password) # gmail
gdoc_in1= etl.component.input.gdoc_in(gdoc_connector, file_path='/home/tiny/Desktop/')

#fileconnector_partner=etl.connector.localfile('/home/tiny/Desktop/partner1.csv')

fileconnector_output=etl.connector.localfile('output/gdoc.csv','r+')

#csv_in1= etl.component.input.csv_in(fileconnector_partner,name='Partner Data')
csv_out1= etl.component.output.csv_out(fileconnector_output,name='Partner OUT Data1')
log1=etl.component.transform.logger(name='Read Partner File')

tran=etl.transition(gdoc_in1, log1)
#tran=etl.transition(log1, csv_in1)
tran1=etl.transition(log1, csv_out1)

job1=etl.job([gdoc_in1,csv_out1], name="dd")

job1.run()