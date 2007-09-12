import wizard
import netsvc
import pooler

def _wo_check(self, cr, uid, data, context):
	pool = pooler.get_pool(cr.dbname)
	print data
	for ab in pool.get('auction.lots').read(cr,uid,data['ids'],['auction_id']):
		if not ab.get('auction_id',False):
			raise wizard.except_wizard('Error!','No Auction Date selected for this  Lot')
	return 'report'

class wizard_report(wizard.interface):
	states = {
		'init': {
			'actions': [],
			'result' : {'type': 'choice', 'next_state': _wo_check }
		},
		'report': {
			'actions': [],
			'result': {'type':'print', 'report':'auction.cat_flagy', 'state':'end'}
		}
	}
wizard_report('auction.catalog.flagey')
