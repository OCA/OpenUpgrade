import time
import campaign

from osv import fields
from osv import osv

AVAILABLE_STATES = [
    ('draft','Draft'),
    ('open','Open'),
    ('freeze', 'Freeze'),
    ('closed', 'Close')
]

class dm_product(osv.osv):
    _name = "dm.product"
    _rec_name = 'product_id'
    _columns = {
        'product_id' : fields.many2one('product.product', 'Product', required=True),
        'qty_planned' : fields.integer('Planned Quantity'),
        'qty_real' : fields.float('Real Quantity'),
        'price' : fields.float('Sale Price')
    }
dm_product()


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
        'name' : fields.char('Name', size=64, required=True),
        'complete_name' : fields.function(_name_get_fnc, method=True, type='char', string='Category'),
        'parent_id' : fields.many2one('dm.offer.document.category', 'Parent'),
        'copywriter_id' : fields.many2one('res.partner', 'Copywriter')
    }
    
dm_offer_document_category()

class dm_offer_document(osv.osv):
    _name = "dm.offer.document"
    _rec_name = 'name'
    _columns = {
        'name' : fields.char('Name', size=64, required=True),
        'code' : fields.char('Code', size=16, required=True),
        'lang_id' : fields.many2one('res.lang', 'Language'),
        'copywriter_id' : fields.many2one('res.partner', 'Copywriter'),
        'category_ids' : fields.many2many('dm.offer.document.category','dm_offer_document_rel', 'doc_id', 'category_id', 'Categories'),
        'mailing_at_dates' : fields.boolean('Mailing at dates'),
        'interactive' : fields.boolean('Interactive'),
        'answer_letter' : fields.boolean('Answer letter'),
        'dtp_operator' : fields.many2one('res.partner', 'Operator'),
        'dtp_theorical_date' : fields.date('Theorical Date'),
        'dtp_valid_date' : fields.date('Valid Date'),
        'dtp_making_date' : fields.date('Making Date'),
        'dtp_reread' : fields.date('Reread Date'),
    }
 
dm_offer_document()

class dm_offer_step(osv.osv):
    _name = "dm.offer.step"
    _order = "sequence"
    _rec_name = 'name'
    
    def __history(self, cr, uid, cases, keyword, context={}):
        for case in cases:
            data = {
                'user_id': uid,
                'state' : keyword,
                'step_id': case.id,
                'date' : time.strftime('%Y-%m-%d')
            }
            obj = self.pool.get('dm.offer.step.history')
            obj.create(cr, uid, data, context)
        return True
    
    def _offer_code(self, cr, uid, ids, name, args, context={}):
        result ={}
        for id in ids:
            code=''
            offer_step = self.browse(cr,uid,[id])[0]
            code = '_'.join([offer_step.offer_id.code,(str(offer_step.sequence) or ''),(offer_step.type or '')])
            result[id]=code
        return result
    _columns = {
        'offer_id' : fields.many2one('dm.offer', 'Offer',required=True, ondelete="cascade"),
        'legal_state' : fields.char('Legal State', size=32),
        'name' : fields.char('Name', size=64, required=True),
        'code' : fields.function(_offer_code,string='Code',type="char",method=True,readonly=True),
        'quotation' : fields.char('Quotation', size=16),
        'media_id' : fields.many2one('dm.media', 'Media'),
        'type' : fields.char('Type', size=16),
        'origin_id' : fields.many2one('dm.offer.step', 'Origin'),
#        'wrkitem_id' : fields.one2many('dm.offer.step.workitem','step_id', 'WorkItems'),
        'notes' : fields.text('Notes'),
        'document_ids' : fields.many2many('dm.offer.document', 'dm_offer_step_rel', 'step_id', 'doc_id', 'Documents'),
        'flow_start' : fields.boolean('Flow Start'),
        'flow_stop' : fields.boolean('Flow Stop'),
        'sequence' : fields.integer('Sequence', required=True),
        'history_ids' : fields.one2many('dm.offer.step.history', 'step_id', 'History'),
        'product_ids' : fields.many2many('dm.product','dm_offer_step_product_rel','offer_step_id','product_id','Products'),
        'state' : fields.selection(AVAILABLE_STATES, 'Status', size=16, readonly=True),
        'incoming_transition_ids' : fields.one2many('dm.offer.step.transition','step_to', 'Incoming Transition'),
        'outgoing_transition_ids' : fields.one2many('dm.offer.step.transition','step_from', 'Outgoing Transition'),
        'split_mode' : fields.selection([('and','And'),('or','Or'),('xor','Xor')],'Split mode'),
        'join_mode' : fields.selection([('and','And'),('xor','Xor')],'Join mode'),
    }

    _defaults = {
        'state': lambda *a : 'draft',
		'split_mode' : lambda *a : 'xor',
		'join_mode' : lambda *a : 'xor',
    }
    
    def state_close_set(self, cr, uid, ids, *args):
        cases = self.browse(cr, uid, ids)
        cases[0].state 
        self.__history(cr,uid, cases, 'closed')
        self.write(cr, uid, ids, {'state':'closed'})
        return True  

    def state_open_set(self, cr, uid, ids, *args):
        cases = self.browse(cr, uid, ids)
        cases[0].state 
        self.__history(cr,uid, cases, 'open')
        self.write(cr, uid, ids, {'state':'open'})
        return True 
    
    def state_freeze_set(self, cr, uid, ids, *args):
        cases = self.browse(cr, uid, ids)
        cases[0].state 
        self.__history(cr,uid, cases, 'freeze')
        self.write(cr, uid, ids, {'state':'freeze'})
        return True
    
    def state_draft_set(self, cr, uid, ids, *args):
        cases = self.browse(cr, uid, ids)
        cases[0].state 
        self.__history(cr,uid, cases, 'draft')
        self.write(cr, uid, ids, {'state':'draft'})
        return True  
    
dm_offer_step()


class dm_offer_step_transition(osv.osv):
    _name = "dm.offer.step.transition"
    _rec_name = 'name'
    _columns = {
        'name' : fields.char('Name', size=64, required=True),
        'condition' : fields.selection([('true','True'),('purchased','Purchased'),('notpurchased','Not Purchased')], 'Condition'),
        #'delay' : fields.integer('Delay'),
        'delay_id' : fields.many2one('dm.offer.delay', 'Offer Delay'),
        'step_from' : fields.many2one('dm.offer.step','From Offer Step'),
        'step_to' : fields.many2one('dm.offer.step','To Offer Step'),
    }
    
dm_offer_step_transition()
class dm_offer_step_history(osv.osv):
    _name = "dm.offer.step.history"
    _order = 'date'
    _columns = {
        'step_id' : fields.many2one('dm.offer.step', 'Offer'),
        'user_id' : fields.many2one('res.users', 'User'),
        'state' : fields.selection(AVAILABLE_STATES, 'Status', size=16),
        'date' : fields.date('Date')
    }
    
    _defaults = {
        'date' : lambda *a: time.strftime('%Y-%m-%d'),
    }

dm_offer_step_history()

class dm_offer_step_workitem(osv.osv):
    _name = "dm.offer.step.workitem"
    _columns = {
        'step_id' : fields.many2one('dm.offer.step', 'Offer Step',required=True, ondelete="cascade"),
        'segment_id' : fields.many2one('dm.campaign.proposition.segment', 'Segments', required=True, ondelete="cascade"),
        'customer_id' : fields.many2one('dm.customer', 'Customer', ondelete="cascade"),
        'date_next_action' : fields.date('Next Action'),
        'purchase_amount' : fields.float('Amount', digits=(16,2))
    }
    
dm_offer_step_workitem()

