import netsvc

import pooler
import time
from report import report_sxw
from osv import osv

class report_comp_mix(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
		super( report_comp_mix, self).__init__(cr, uid, name, context)
		self.localcontext.update({
				'time': time,
		})

report_sxw.report_sxw('report.comp_mix','form.mix','addons/labo_stock/report/report_comp.rml',parser=report_comp_mix)

