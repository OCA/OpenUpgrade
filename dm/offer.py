import time

from osv import fields
from osv import osv

AVAILABLE_STATES = [
    ('draft','Draft'),
    ('open','Open'),
    ('freeze', 'Freeze'),
    ('closed', 'Close')
]
class dm_offer_category(osv.osv):
    _name = "dm.offer.category"

    def name_get(self, cr, uid, ids, context={}):
        if not len(ids):
            return []
        reads = self.read(cr, uid, ids, ['name','parent_id'], context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1]+' / '+name
            res.append((record['id'], name))
        return res

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = self.name_get(cr, uid, ids)
        return dict(res)
    
    def _check_recursion(self, cr, uid, ids):
        level = 100
        while len(ids):
            cr.execute('select distinct parent_id from dm_offer_category where id in ('+','.join(map(str,ids))+')')
            ids = filter(None, map(lambda x:x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True     

    _columns = {
        'complete_name' : fields.function(_name_get_fnc, method=True, type='char', string='Category'),
        'parent_id' : fields.many2one('dm.offer.category', 'Parent'),
        'name' : fields.char('Category Name', size=64),
        'domain' : fields.selection([('view','View'),('general','General'),('production','Production'),('purchase','Purchase')], 'Category Domain')
                }
    
    _constraints = [
        (_check_recursion, 'Error ! You can not create recursive categories.', ['parent_id'])
    ]
        
dm_offer_category()

class dm_offer_production_cost(osv.osv):
    _name = "dm.offer.production.cost"
    _columns = {
        'name' : fields.char('Name', size=32, required=True)
                }               
    
dm_offer_production_cost()

class dm_offer_delay(osv.osv):
    _name = "dm.offer.delay"
    _columns = {
        'name' : fields.char('Name', size=32, required=True)
                }
    
dm_offer_delay()

class dm_offer(osv.osv):
    _name = "dm.offer"
    _columns = {
        'state': fields.selection(AVAILABLE_STATES, 'Status', size=16, readonly=True),
        'history_ids' : fields.one2many('dm.offer.history', 'offer_id', 'History'),
        'production_cost' : fields.many2one('dm.offer.production.cost', 'Production Cost'),
        'category_ids' : fields.many2one('dm.offer.category', 'Categories', domain="[('domain','=','general')]"),
        'production_category_ids' : fields.many2one('dm.offer.category', 'Production Categories' , domain="[('domain','=','production')]"),
        'purchase_category_ids' : fields.many2one('dm.offer.category', 'Purchase Categories', domain="[('domain','=','purchase')]"),
        'active' : fields.boolean('Active')
                }
    
    _defaults = {
        'active': lambda *a: 1,
        'state': lambda *a: 'draft',
                 }
    
dm_offer()

class dm_offer_history(osv.osv):
    _name = "dm.offer.history"
    _order = 'date'
    _columns = {
        'offer_id' : fields.many2one('dm.offer', 'Offer', required=True, ondelete="cascade"),
        'date' : fields.date('Date'),
        'user_id' : fields.many2one('res.users', 'User'),
        'state': fields.selection(AVAILABLE_STATES, 'Status', size=16)
                }
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d'),
    }   
dm_offer_history()