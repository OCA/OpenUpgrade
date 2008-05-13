import time

from osv import fields
from osv import osv

#print dir(offer)
#print dir(offer.dm_offer_category)

AVAILABLE_STATES = [
    ('draft','Draft'),
    ('open','Open'),
    ('freeze', 'Freeze'),
    ('closed', 'Close')
]

class dm_offer_step_transition(osv.osv):
    _name = "dm.offer.step.transition"
    _columns = {
        'condition' : fields.selection([('true','True'),('purchased','Purchased'),('notpurchased','Not Purchased')], 'Condition'),
        'delay' : fields.integer('Delay'),
        'delay_id' : fields.many2one('dm.offer.delay', 'Offer Delay')
                }
    
dm_offer_step_transition()

class dm_offer_document_category(osv.osv):
    _name = "dm.offer.document.category"
    _rec_name = "name"
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
        
    _columns = {
        'name' : fields.char('Category Name', size=64),
        'complete_name' : fields.function(_name_get_fnc, method=True, type='char', string='Category'),
        'parent_id' : fields.many2one('dm.offer.document.category', 'Parent'),
        'copywrite_id' : fields.many2one('res.partner', 'Copywriter')
                }
    
dm_offer_document_category()

class dm_offer_document(osv.osv):
    _name = "dm.offer.document"
    _columns = {
        'category_ids' : fields.many2many('dm.offer.document.category','dm_offer_document_rel', 'doc_id', 'category_id', 'Categories'),
        'mailing_at_dates' : fields.boolean('Mailing at dates'),
        'interactive' : fields.boolean('Interactive'),
        'answer_letter' : fields.boolean('Answer letter'),
#        'pao_reread' : fields.
                }
 
dm_offer_document()

class dm_offer_step(osv.osv):
    _name = "dm.offer.step"
    _order = "sequence"
    rec_name = 'sequence'
    _columns = {
        'document_ids' : fields.many2many('dm.offer.document', 'dm_offer_step_rel', 'step_id', 'doc_id', 'Documents'),
        'flow_start' : fields.boolean('Flow Start'),
        'flow_stop' : fields.boolean('Flow Stop'),
        'sequence' : fields.integer('Sequence'),
        'history_ids' : fields.one2many('dm.offer.step.history', 'step_id', 'History'),
        'state' : fields.selection(AVAILABLE_STATES, 'Status', size=16, readonly=True),
                }

    _defaults = {
        'state': lambda *a : 'draft',
                 }
dm_offer_step()


class dm_offer_step_history(osv.osv):
    _name = "dm.offer.step.history"
    _order = 'create_date'
    _columns = {
        'step_id' : fields.many2one('dm.offer.step', 'Offer'),
        'user_id' : fields.many2one('res.users', 'User'),
        'state' : fields.selection(AVAILABLE_STATES, 'Status', size=16),
        'create_date' : fields.date('Date')
                }
    
    _defaults = {
        'create_date' : lambda *a: time.strftime('%Y-%m-%d'),
                 }

dm_offer_step_history()

class dm_offer_step_workitem(osv.osv):
    _name = "dm.offer.step.workitem"
    _columns = {
        'step_id' : fields.many2one('dm.offer.step', 'Offer'),
#        'segment_id' : fields.many2one(),
#        'customer_id' : fields.many2one('dm.customer', 'Customer'),
        'date_next_action' : fields.date('Next Action'),
        'purchase_amount' : fields.float('Amount', digits=(16,2))
                }
    
dm_offer_step_workitem()