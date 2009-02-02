import etl

fileconnector_partner=etl.connector.file_connector.file_connector('data/partner.csv')
fileconnector_partner1=etl.connector.file_connector.file_connector('data/partner1.csv')
fileconnector_partner3=etl.connector.file_connector.file_connector('data/partner3.csv')
csv_in1= etl.component.input.csv_in.csv_in('Partner Data',fileconnector_partner)
csv_in2= etl.component.input.csv_in.csv_in('Partner Data1',fileconnector_partner1)
csv_out1= etl.component.output.csv_out.csv_out('data/partner3.csv')
sort1=etl.component.transform.sort.sort('name')
log1=etl.component.transform.logger.logger(name='Read Partner File')
log2=etl.component.transform.logger.logger(name='After Sort')
sleep1=etl.component.control.sleep.sleep(1)

tran=etl.etl.transition(csv_in1,sort1)
tran1=etl.etl.transition(csv_in2,sort1)
tran4=etl.etl.transition(sort1,sleep1)
tran4=etl.etl.transition(sleep1,log2)
tran6=etl.etl.transition(sleep1,log1,channel_source="statistics")
tran5=etl.etl.transition(sort1,csv_out1)


job1=etl.etl.job([csv_out1,log2,log1])
job1.run()

