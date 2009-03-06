#!/usr/bin/python
import sys
sys.path.append('..')
import etl
from etl import transformer
fileconnector_partner=etl.connector.localfile('input/partner.csv')
csv_in1= etl.component.input.csv_in(fileconnector_partner,name='Partner Data')


unique = etl.component.transform.unique()
log1=etl.component.transform.logger(name='main')
log2=etl.component.transform.logger(name='duplicate')

tran=etl.transition(csv_in1,unique)

tran1=etl.transition(unique,log2,channel_source='duplicate')
tran1=etl.transition(unique,log1,channel_source='main')

job1=etl.job([log2,log1])
job1.run()



