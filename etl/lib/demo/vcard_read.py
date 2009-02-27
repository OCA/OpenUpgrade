#!/usr/bin/python
import sys
sys.path.append('..')

import etl

fileconnector_partner=etl.connector.localfile('input/input.vcf')
vcard_in1= etl.component.input.vcard_in(fileconnector_partner)
log1=etl.component.transform.logger(name='Read Vcard File')

tran=etl.transition(vcard_in1,log1)
job1=etl.job([log1])
job1.run()
