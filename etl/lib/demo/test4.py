#!/usr/bin/python

import sys
sys.path.append('..')

import etl

sqlconnector_partner=etl.connector.sql_connector('localhost',5432, 'trunk', 'fp', 'fp')

sql_in1= etl.component.input.sql_in(
    sqlconnector_partner,'select * from res_partner where id<=10 order by id')

log1=etl.component.transform.logger(name='Read Partner')


tran=etl.transition(sql_in1,log1)

job1=etl.job([log1])
job1.run()

