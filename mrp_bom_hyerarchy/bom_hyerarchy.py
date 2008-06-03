from osv import fields
from osv import osv

class mrp_bom(osv.osv):
	_inherit = 'mrp.bom'
	def _child_compute(self, cr, uid, ids, name, arg, context={}):
		result = {}
		for bom in self.browse(cr, uid, ids, context=context):
			result[bom.id] = map(lambda x: x.id, bom.bom_lines)
			ok = ((name=='child_complete_ids') and (bom.product_id.supply_method=='produce'))
			if bom.type=='phantom' or ok:
				sids = self.pool.get('mrp.bom').search(cr, uid, [('bom_id','=',False),('product_id','=',bom.product_id.id)])
				if sids:
					bom2 = self.pool.get('mrp.bom').browse(cr, uid, sids[0], context=context)
					result[bom.id] += map(lambda x: x.id, bom2.bom_lines)
		return result
	_columns = {
		'child_ids': fields.function(_child_compute,relation='mrp.bom', method=True, string="BoM Hyerarchy", type='many2many'),
		'child_complete_ids': fields.function(_child_compute,relation='mrp.bom', method=True, string="BoM Hyerarchy", type='many2many')
	}
mrp_bom()
