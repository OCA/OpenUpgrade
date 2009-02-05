#!/usr/bin/python

import sys
sys.path.append('..')

import etl

sqlconnector_partner=etl.connector.sql_connector.sql_connector('localhost',5432, 'panimpex', 'postgres', 'postgres')
sql_in1= etl.component.input.sql_in.sql_in('Partner Data',sqlconnector_partner,'select * from res_partner where id<=10 order by id')

log1=etl.component.transform.logger.logger(name='Read Partner')


tran=etl.transition.transition(sql_in1,log1)

job1=etl.job.job('job1',[log1])
job1.run()

