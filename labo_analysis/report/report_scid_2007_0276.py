import netsvc
import pooler
import time
from report import report_sxw

class report_scid(report_sxw.rml_parse):

	 def __init__(self, cr, uid, name, context):
		super(report_scid, self).__init__(cr, uid, name, context)
		self.localcontext.update({
				'time': time,
				'get_sample':self.get_sample
		  })

	 def get_sample(self,request):
		print "request obje",request.id
		self.cr.execute('select count(id) from labo_sample where sample_id=%d'%(request.id,))
		res = self.cr.fetchone()
		return str(res[0] or 0)

report_sxw.report_sxw('report.List_scid', 'labo.analysis.request', 'addons/labo_analysis/report/report_scid_2007_0276.rml',parser=report_scid)


