#!/usr/bin/python

import sys
sys.path.append('..')

import etl


fileconnector_partner=etl.connector.file_connector.file_connector('input/partner.csv')
fileconnector_partner2=etl.connector.file_connector.file_connector('input/partner2.csv')

in1 = etl.component.input.csv_in.csv_in('Partner Data',fileconnector_partner)
in2 = etl.component.input.csv_in.csv_in('Partner Data2',fileconnector_partner2)
diff1 = etl.component.transform.diff.diff('Diff1',['id'])

log_1 = etl.component.transform.logger_bloc.logger_bloc(name="Original Data")
log_2 = etl.component.transform.logger_bloc.logger_bloc(name="Modified Data")

log1 = etl.component.transform.logger.logger(name="Log Same")
log2 = etl.component.transform.logger.logger(name="Log Add")
log3 = etl.component.transform.logger.logger(name="Log Remove")
log4 = etl.component.transform.logger.logger(name="Log Update")

fileconnector_output=etl.connector.file_connector.file_connector('output/test2_add.csv')
csv_out1 = etl.component.output.csv_out.csv_out('Output',fileconnector_output)

etl.etl.transition(in1, log_1)
etl.etl.transition(in2, log_2)

etl.etl.transition(in1, diff1, channel_destination='original')
etl.etl.transition(in2, diff1, channel_destination='modified')

etl.etl.transition(diff1, log1, channel_source="same")
etl.etl.transition(diff1, log3, channel_source="remove")
etl.etl.transition(diff1, log2, channel_source="add")
etl.etl.transition(diff1, csv_out1, channel_source="add")
etl.etl.transition(diff1, log4, channel_source="update")

job = etl.etl.job('job2',[log_1,log_2,diff1,log1,log2,log3,log4,csv_out1])
job.run()

