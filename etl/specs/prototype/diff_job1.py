#! /usr/bin/python

import etl

in1 = etl.operator.etl_csv_input('data/partner.csv', is_start=True)
in2 = etl.operator.etl_csv_input('data/partner2.csv', is_start=True)
diff1 = etl.operator.etl_operator_diff(['id'])

log_1 = etl.operator.etl_operator_log_bloc(name="Original Data")
log_2 = etl.operator.etl_operator_log_bloc(name="Modified Data")

log1 = etl.operator.etl_operator_log(name="Log Same")
log2 = etl.operator.etl_operator_log(name="Log Add")
log3 = etl.operator.etl_operator_log(name="Log Remove")
log4 = etl.operator.etl_operator_log(name="Log Update")


csv1 = etl.operator.etl_csv_output('intermediate/add.csv')

etl.transition(in1, log_1)
etl.transition(in2, log_2)

etl.transition(in1, diff1, 'original')
etl.transition(in2, diff1, 'modified')

etl.transition(diff1, log1, channel_source="same")
etl.transition(diff1, log3, channel_source="remove")
etl.transition(diff1, log2, channel_source="add")
etl.transition(diff1, csv1, channel_source="add")
etl.transition(diff1, log4, channel_source="update")

job = etl.job([in1,in2,diff1])
job.run()

