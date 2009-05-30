#!/usr/bin/python

import sys
sys.path.append('..')

import etl
from etl import transformer

fileconnector=etl.connector.localfile('input/invoice.csv')
trans=transformer(
    {
        'id':transformer.LONG,
        'name':transformer.STRING,
        'invoice_date':transformer.DATE,
        'invoice_amount':transformer.FLOAT,
        'is_paid':transformer.BOOLEAN
    }
)
csv_in1= etl.component.input.csv_in(fileconnector=fileconnector,transformer=trans)
log1=etl.component.transform.logger(name='Read Invoice File')
tran=etl.transition(csv_in1,log1)
job1=etl.job([csv_in1,log1])
job1.run()
