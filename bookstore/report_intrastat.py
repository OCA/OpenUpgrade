from osv import osv

class report_intrastat_code(osv.osv):
	_inherit = "report.intrastat.code"

	def name_get(self, cr, user, ids, context={}):
		if not len(ids):
			return []
		def formating(r):
			if r['description'] and r['name']:
				return(r['id'], r['description']+' - '+r['name'])
			return(r['id'], (r['description'] or '')+(r['name'] or ''))
		
		return [formating(r) for r in self.read(cr, user, ids, ['name','description'], context)]

	_sql_constraints = [
				('both_not_null', 'CHECK (name is not null or description is not null)', \
				 'Please provide at least a code or a description')]

report_intrastat_code()
