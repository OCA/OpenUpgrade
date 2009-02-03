#!/usr/bin/python

import sys
sys.path.append('..')

import etl
<<<<<<< TREE
from etl import etl
from etl import component

csv_in1= etl.component.input.csv_in('data/partner.csv')
csv_in2= etl.component.input.csv_in('data/partner1.csv')
csv_out1= etl.component.output.csv_out('data/partner3.csv')
sort1=etl.component.transfer.sort('name')
log1=etl.component.transfer.logger(name='Read Partner File')
log2=etl.component.transfer.logger(name='After Sort')
sleep1=etl.component.control.sleep(1)

tran=etl.transition(csv_in1,sort1)
tran1=etl.transition(csv_in2,sort1)
tran4=etl.transition(sort1,sleep1)
tran4=etl.transition(sleep1,log2)
tran5=etl.transition(sort1,csv_out1)


job1=etl.job([csv_out1,log2])
=======

fileconnector_partner=etl.connector.file_connector.file_connector('input/partner.csv')
fileconnector_partner1=etl.connector.file_connector.file_connector('input/partner1.csv')
fileconnector_partner3=etl.connector.file_connector.file_connector('input/partner3.csv')
csv_in1= etl.component.input.csv_in.csv_in('Partner Data',fileconnector_partner)
csv_in2= etl.component.input.csv_in.csv_in('Partner Data1',fileconnector_partner1)
csv_out1= etl.component.output.csv_out.csv_out('Partner OUT Data1','output/test1_partner.csv')
sort1=etl.component.transform.sort.sort('sort1','name')
log1=etl.component.transform.logger.logger(name='Read Partner File')
log2=etl.component.transform.logger.logger(name='After Sort')
sleep1=etl.component.control.sleep.sleep('sleep1',1)

tran=etl.etl.transition(csv_in1,sort1)
tran1=etl.etl.transition(csv_in2,sort1)
tran4=etl.etl.transition(sort1,sleep1)
tran4=etl.etl.transition(sleep1,log2)
#tran6=etl.etl.transition(sleep1,log1,channel_source="statistics")
tran5=etl.etl.transition(sort1,csv_out1)


<<<<<<< TREE
<<<<<<< TREE
job1=etl.etl.job([csv_out1,log2])
>>>>>>> MERGE-SOURCE
=======
job1=etl.etl.job([csv_out1,log2,log1])
>>>>>>> MERGE-SOURCE
=======
job1=etl.etl.job('job1',[csv_out1,log2])
>>>>>>> MERGE-SOURCE
job1.run()

