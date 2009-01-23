import etl

csv_in1= etl.component.input.csv_in.csv_in('data/partner.csv')
csv_in2= etl.component.input.csv_in.csv_in('data/partner1.csv')
csv_out1= etl.component.output.csv_out.csv_out('data/partner3.csv')
sort1=etl.component.transform.sort.sort('name')
log1=etl.component.transform.logger.logger(name='Read Partner File')
log2=etl.component.transform.logger.logger(name='After Sort')
sleep1=etl.component.control.sleep.sleep(1)

tran=etl.etl.transition(csv_in1,sort1)
tran1=etl.etl.transition(csv_in2,sort1)
tran4=etl.etl.transition(sort1,sleep1)
tran4=etl.etl.transition(sleep1,log2)
tran5=etl.etl.transition(sort1,csv_out1)


job1=etl.etl.job([csv_out1,log2])
job1.run()

