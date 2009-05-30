#!/usr/bin/python
import etl

sort1=etl.component.transform.sort('name')
log1=etl.component.transform.logger(name='Read Partner File')
log2=etl.component.transform.logger(name='After Sort')
sleep1=etl.component.control.sleep()

tran0=etl.transition(log1,sort1)
tran1=etl.transition(sort1,sleep1)
tran2=etl.transition(sleep1,log2)
job1=etl.job([log1,sort1,sleep1,log2])


fileconnector_partner=etl.connector.localfile('input/partner.csv')
csv_in1= etl.component.input.csv_in(fileconnector_partner,name='Partner Data')

fileconnector_output=etl.connector.localfile('output/subjob_partner.csv','w+')
csv_out1= etl.component.output.csv_out(fileconnector_output,name='Partner OUT Data1')

subjob = etl.component.transform.subjob(job1)

tran0=etl.transition(csv_in1,subjob)
tran1=etl.transition(subjob,csv_out1)

job2 = etl.job([subjob,csv_in1,csv_out1])
job2.run()
