#!/usr/bin/python

import sys
sys.path.append('..')

import etl

fileconnector_partner=etl.connector.file_connector.file_connector('input/partner.csv')
fileconnector_partner1=etl.connector.file_connector.file_connector('input/partner1.csv')
fileconnector_partner3=etl.connector.file_connector.file_connector('input/partner3.csv')
fileconnector_output=etl.connector.file_connector.file_connector('output/test1_partner.csv')
csv_in1= etl.component.input.csv_in.csv_in('Partner Data',fileconnector_partner)
csv_in2= etl.component.input.csv_in.csv_in('Partner Data1',fileconnector_partner1)
csv_out1= etl.component.output.csv_out.csv_out('Partner OUT Data1',fileconnector_output)
sort1=etl.component.transform.sort.sort('sort1','name')
log1=etl.component.transform.logger.logger(name='Read Partner File')
log2=etl.component.transform.logger.logger(name='After Sort')
sleep1=etl.component.control.sleep.sleep('sleep1')

tran=etl.transition.transition(csv_in1,sort1)
tran1=etl.transition.transition(csv_in2,sort1)
tran4=etl.transition.transition(sort1,sleep1)
tran4=etl.transition.transition(sleep1,log2)
#tran6=etl.etl.transition(sleep1,log1,channel_source="statistics")
tran5=etl.transition.transition(sort1,csv_out1)


job1=etl.job.job('job1',[csv_out1,log2])
job1.run()

