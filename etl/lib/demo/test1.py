import etl
from etl import etl
from etl import component

csv_in1= etl.component.input.csv_in('data/partner.csv')
csv_in2= etl.component.input.csv_in('data/partner1.csv')
csv_out1= etl.component.output.csv_out('data/partner3.csv')
sort1=etl.component.transfer.sort('name')
log1=etl.component.transfer.logger(name='Read Partner File')
log2=etl.component.transfer.logger(name='After Sort')
sleep1=etl.component.control.sleep(1)

tran=etl.transition(csv_in1,sort1)
tran1=etl.transition(csv_in2,sort1)
tran4=etl.transition(sort1,sleep1)
tran4=etl.transition(sleep1,log2)
tran5=etl.transition(sort1,csv_out1)


job1=etl.job([csv_out1,log2])
job1.run()
