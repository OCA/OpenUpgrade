import netsvc
import pooler
import time
from report import report_sxw

class report_dna_horse(report_sxw.rml_parse):

	 def __init__(self, cr, uid, name, context):
		super(report_dna_horse, self).__init__(cr, uid, name, context)
		self.localcontext.update({
				'time': time,
		  })
report_sxw.report_sxw('report.report_dna', 'labo.dog', 'addons/labo_analysis/report/report_dna.rml',parser=report_dna_horse, header=False)
report_sxw.report_sxw('report.report_dna_dogs', 'labo.dog', 'addons/labo_analysis/report/report_dna_dogs.rml',parser=report_dna_horse, header=False)
report_sxw.report_sxw('report.report_dna_dogs_logo', 'labo.dog', 'addons/labo_analysis/report/report_dna_dogs_logo.rml',parser=report_dna_horse, header=False)


