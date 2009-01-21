import etl
from etl import etl
from etl import component


in1 = component.csv_in('data/partner.csv')
in2 = component.csv_in('data/partner2.csv')
diff1 = component.diff(['id'])

log_1 = component.logger_bloc(name="Original Data")
log_2 = component.logger_bloc(name="Modified Data")

log1 = component.logger(name="Log Same")
log2 = component.logger(name="Log Add")
log3 = component.logger(name="Log Remove")
log4 = component.logger(name="Log Update")


csv_out1 = component.csv_out('data/add.csv')

etl.transition(in1, log_1)
etl.transition(in2, log_2)

etl.transition(in1, diff1, channel_destination='original')
etl.transition(in2, diff1, channel_destination='modified')

etl.transition(diff1, log1, channel_source="same")
etl.transition(diff1, log3, channel_source="remove")
etl.transition(diff1, log2, channel_source="add")
etl.transition(diff1, csv_out1, channel_source="add")
etl.transition(diff1, log4, channel_source="update")

job = etl.job([log_1,log_2,diff1,log1,log2,log3,log4,csv_out1])
job.run()

