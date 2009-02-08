#! /usr/bin/python

import etl

in1 = etl.operator.etl_csv_input('data/partner.csv', is_start=True)
out1 = etl.operator.etl_csv_output('output/partner.csv')
log1 = etl.operator.etl_operator_log(name='PartnerLogger')
log2 = etl.operator.etl_operator_log(name='OuputLogger')
sort1 = etl.operator.etl_operator_sort('name')

etl.transition(in1, log1)
etl.transition(log1, out1)
etl.transition(out1, sort1)
etl.transition(sort1, log2)

job = etl.job([in1,out1])
job.run()

