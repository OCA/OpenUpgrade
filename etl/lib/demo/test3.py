import etl

fileconnector=etl.connector.file_connector.file_connector('data/invoice.csv')
transformer_description= {'id':etl.transformer.LONG,'name':etl.transformer.STRING,'invoice_date':etl.transformer.DATE,'invoice_amount':etl.transformer.FLOAT,'is_paid':etl.transformer.BOOLEAN}    
transformer=etl.transformer(transformer_description)
csv_in1= etl.component.input.csv_in.csv_in('Invoice File',fileconnector=fileconnector,transformer=transformer)
log1=etl.component.transform.logger.logger(name='Read Invoice File')
tran=etl.etl.transition(csv_in1,log1)
job1=etl.etl.job('job of test3',[log1])
job1.run()

