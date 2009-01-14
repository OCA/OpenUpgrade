#! /usr/bin/python

import etl

in1 = etl.operator.etl_csv_input('data/partner3.csv', is_start=True)
in2 = etl.operator.etl_csv_input('intermediate/add.csv', is_start=True)

merge1 = etl.operator.etl_merge()

log1 = etl.operator.etl_operator_log_bloc(name="Original Data")
log2 = etl.operator.etl_operator_log_bloc(name="Final Data")

etl.transition(in1, merge1)
etl.transition(in1, log1)

etl.transition(in2, merge1)

etl.transition(merge1, log2)

job = etl.job([in1,in2,merge1])
job.run()

