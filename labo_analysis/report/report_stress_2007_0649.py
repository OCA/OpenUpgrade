import netsvc
import pooler
import time
from report import report_sxw
from osv import osv

class report_stress(report_sxw.rml_parse):
	
	def __init__(self, cr, uid, name, context):
		super( report_stress, self).__init__(cr, uid, name, context)
		self.localcontext.update({
				'time': time,
#				'nb_items':self.nb_items
				'get_number':self.get_number,
				'get_kind':self.get_kind,
				'get_cond_pack':self.get_cond_pack,
				'get_cond_recept':self.get_cond_recept,
				'get_nature':self.get_nature

		})
	def get_number(self,request):
		self.cr.execute('select count(1) from labo_sample where sample_id=%d'%(request.id,))
		res = [ x[0] for x in self.cr.fetchall() if x[0]]
		return ",".join([str(x) for x in res])

	def get_kind(self,request):
		self.cr.execute('select distinct(kind) from labo_sample where sample_id=%d'%(request.id,))
		res = [ x[0] for x in self.cr.fetchall() if x[0]]
		return ",".join([str(x) for x in res])


	def get_cond_pack(self,request):
		self.cr.execute('select distinct(cond_packing) from labo_sample where sample_id=%d'%(request.id,))
		res = [ x[0] for x in self.cr.fetchall() if x[0]]
		return ",".join([str(x) for x in res])

	def get_cond_recept(self,request):
		self.cr.execute('select distinct(cond_reception) from labo_sample where sample_id=%d'%(request.id,))
		res = [ x[0] for x in self.cr.fetchall() if x[0]]
		return ",".join([str(x) for x in res])

	def get_nature(self,request):
		self.cr.execute('select distinct(nature) from labo_sample where sample_id=%d'%(request.id,))
		res = [ x[0] for x in self.cr.fetchall() if x[0]]
		return ",".join([str(x) for x in res])
		 

report_sxw.report_sxw('report.List_stress','labo.analysis.request','addons/labo_analysis/report/report_stress_2007_0649.rml',parser=report_stress)
