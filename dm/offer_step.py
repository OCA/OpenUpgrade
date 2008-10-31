# -*- encoding: utf-8 -*-
import time
import campaign

from osv import fields
from osv import osv
import datetime

AVAILABLE_STATES = [
    ('draft','Draft'),
    ('open','Open'),
    ('freeze', 'Freeze'),
    ('closed', 'Close')
]

AVAILABLE_ITEM_TYPES = [
    ('main','Main Item'),
    ('standart','Standart Item'),
]

class dm_offer_step_type(osv.osv):
    _name="dm.offer.step.type"
    _rec_name = 'name'

    _columns = {
        'name' : fields.char('Name', size=64, translate=True, required=True),
        'code' : fields.char('Code', size=8, translate=True, required=True),
        'flow_start' : fields.boolean('Flow Start'),
        'flow_stop' : fields.boolean('Flow Stop'),
        'description' : fields.text('Description', translate=True),
        }

    _sql_constraints = [
        ('code_uniq', 'UNIQUE(code)', 'The code must be unique!'),
    ]

dm_offer_step_type()

class dm_offer_step(osv.osv):
    _name = "dm.offer.step"

    def __history(self, cr, uid, ids, keyword, context={}):
        for id in ids:
            data = {
                'user_id': uid,
                'state' : keyword,
                'step_id': id,
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
            code = '_'.join([offer_step.offer_id.code,(offer_step.type or '')])
            result[id]=code
        return result

    def _get_offer_step_type(self,cr,uid,context={}):
        offer_step_type = self.pool.get('dm.offer.step.type')
        type_ids = offer_step_type.search(cr,uid,[])
        type = offer_step_type.browse(cr,uid,type_ids)
        return map(lambda x : [x.code,x.code],type)

    _columns = {
        'name' : fields.char('Description',size=64, required=True),
        'offer_id' : fields.many2one('dm.offer', 'Offer',required=True, ondelete="cascade"),
        'parent_id' : fields.many2one('dm.offer', 'Parent'),
        'legal_state' : fields.char('Legal State', size=32),
        'code' : fields.function(_offer_code,string='Code',type="char",method=True,readonly=True),
        'quotation' : fields.char('Quotation', size=16),
        'media_ids' : fields.many2many('dm.media', 'dm_offer_step_media_rel','step_id','media_id', 'Medias'),
        'type' : fields.selection(_get_offer_step_type,'Type',required=True),
        'origin_id' : fields.many2one('dm.offer.step', 'Origin'),
        'desc' : fields.text('Description'),
        'dtp_note' : fields.text('DTP Notes'),
        'dtp_category_ids' : fields.many2many('dm.offer.category','dm_offer_dtp_category','offer_id','offer_dtp_categ_id', 'DTP Categories') ,# domain="[('domain','=','production')]"),
        'trademark_note' : fields.text('Trademark Notes'),
        'trademark_category_ids' : fields.many2many('dm.offer.category','dm_offer_trademark_category','offer_id','offer_trademark_categ_id','Trademark Categories'),# domain="[('domain','=','purchase')]"),
        'production_note' : fields.text('Production Notes'),
        'planning_note' : fields.text('Planning Notes'),
        'purchase_note' : fields.text('Purchase Notes'),
        'mailing_at_dates' : fields.boolean('Mailing at dates'),
        'floating date' : fields.boolean('Floating date'),
        'interactive' : fields.boolean('Interactive'),
#        'wrkitem_id' : fields.one2many('dm.offer.step.workitem','step_id', 'WorkItems'),
        'notes' : fields.text('Notes'),
        'document_ids' : fields.one2many('dm.offer.document', 'step_id', 'DTP Documents'),
        'flow_start' : fields.boolean('Flow Start'),
        'history_ids' : fields.one2many('dm.offer.step.history', 'step_id', 'History'),
        'product_ids' : fields.one2many('dm.step.product', 'offer_step_id', 'Products'),
        'state' : fields.selection(AVAILABLE_STATES, 'Status', size=16, readonly=True),
        'incoming_transition_ids' : fields.one2many('dm.offer.step.transition','step_to', 'Incoming Transition',readonly=True),
        'outgoing_transition_ids' : fields.one2many('dm.offer.step.transition','step_from', 'Outgoing Transition'),
        'split_mode' : fields.selection([('and','And'),('or','Or'),('xor','Xor')],'Split mode'),
        'doc_number' : fields.integer('Number of documents of the mailing'),
        'manufacturing_constraint_ids': fields.one2many('dm.offer.step.manufacturing_constraint', 'offer_step_id', 'Manufacturing Constraints'),
    }

    _defaults = {
        'state': lambda *a : 'open',
        'split_mode' : lambda *a : 'or',
    }

    def onchange_type(self,cr,uid,ids,type,offer_id):
        step_type_ids= self.pool.get('dm.offer.step.type').search(cr,uid,[('code','=',type)])
        step_type = self.pool.get('dm.offer.step.type').browse(cr,uid,step_type_ids)[0]
        value = {
                    'flow_start':step_type['flow_start'],
                }
        if offer_id :
            offer = self.pool.get('dm.offer').browse(cr,uid,[offer_id])[0]
            if offer.type == 'model':
                value['name'] = step_type.name
            else :
                value['name'] = "%s for %s"% (step_type.code,offer.name) 
        return {'value':value}

    def state_close_set(self, cr, uid, ids, *args):
        self.__history(cr,uid, ids, 'closed')
        self.write(cr, uid, ids, {'state':'closed'})
        return True

    def state_open_set(self, cr, uid, ids, *args):
        self.__history(cr,uid,ids, 'open')
        self.write(cr, uid, ids, {'state':'open'})
        return True

    def state_freeze_set(self, cr, uid, ids, *args):
        self.__history(cr,uid,ids, 'freeze')
        self.write(cr, uid, ids, {'state':'freeze'})
        return True

    def state_draft_set(self, cr, uid, ids, *args):
        self.__history(cr,uid,ids, 'draft')
        self.write(cr, uid, ids, {'state':'draft'})
        return True

dm_offer_step()

class dm_offer_step_transition(osv.osv):
    _name = "dm.offer.step.transition"
    _rec_name = 'condition'
    _columns = {
        'condition' : fields.selection([('automatic','Automatic'),('purchased','Purchased'),('notpurchased','Not Purchased')], 'Condition',required=True),
        'delay' : fields.integer('Offer Delay' ,required=True),
        'step_from' : fields.many2one('dm.offer.step','From Offer Step',required=True, ondelete="cascade"),
        'step_to' : fields.many2one('dm.offer.step','To Offer Step',required=True, ondelete="cascade"),
        'media_id' : fields.many2one('dm.media','Media',required=True)
    }
    def default_get(self, cr, uid, fields, context={}):
        data = super(dm_offer_step_transition, self).default_get(cr, uid, fields, context)
        if context.has_key('type'):
            if not context['step_id']:
                raise osv.except_osv('Error !',"It is necessary to save this offer step before creating a transition")
            data['condition']='automatic'
            data['delay']='0'
            data[context['type']] = context['step_id']
        return data

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
        'step_id': fields.many2one('dm.offer.step', 'Offer Step'),
    }

dm_offer_document()

class dm_offer_step_workitem(osv.osv):
    _name = "dm.offer.step.workitem"
    _columns = {
        'step_id' : fields.many2one('dm.offer.step', 'Offer Step',required=True, ondelete="cascade"),
        'segment_id' : fields.many2one('dm.campaign.proposition.segment', 'Segments', required=True, ondelete="cascade"),
        'customer_id' : fields.many2one('dm.customer', 'Customer', ondelete="cascade"),
        'date_next_action' : fields.date('Next Action'),
        'purchase_amount' : fields.float('Amount', digits=(16,2))
    }
    def create(self, cr, uid, vals, context=None, check=True):
        step = self.pool.get('dm.offer.step').browse(cr,uid,[vals['step_id']])[0]
        if step.outgoing_transition_ids:
            transitions = dict(map(lambda x : (x.id,x.delay),step.outgoing_transition_ids))
            print "DEBUG - Creating new workitem"
            print "DEBUG - transitions items: ", transitions.items()
            print "DEBUG - transitions values: ", transitions.values()
            trans = [(k,v) for k,v in transitions.items() if v == min(transitions.values())][0]
            new_date = datetime.date.today() + datetime.timedelta(trans[1])
            vals['date_next_action'] = new_date
            print "DEBUG - vals : ",vals
        return super(dm_offer_step_workitem, self).create(cr, uid, vals, context)

    def _update_workitem(self, cr, uid, ids=False, context={}):
        '''
        Function called by the sceduler to update workitem from the segments of propositions.
        '''
        """
        print "DEBUG - _update_workitem called by scheduler"
        wrkitem_ids =self.search(cr,uid,[('date_next_action','=',time.strftime('%Y-%m-%d'))])
        wrkitems =self.browse(cr,uid,wrkitem_ids)
        if not wrkitems:
            print "DEBUG - no workitem to update"
            return
        for wrkitem in wrkitems :
            step = wrkitem.step_id
            if step.outgoing_transition_ids:
                transitions = dict(map(lambda x : (x,int(x.delay)),step.outgoing_transition_ids))
                print "DEBUG - transitions items: ", transitions.items()
                print "DEBUG - transitions values: ", transitions.values()
                trans = [k for k,v in transitions.items() if v == min(transitions.values())][0]
                # If relaunching
                if trans.step_to.type == 'RL':
                    prop_id = self.pool.get('dm.campaign.proposition').copy(cr, uid, wrkitem.segment_id.proposition_id.id,
                        {'proposition_type':'relaunching', 'initial_proposition_id':wrkitem.segment_id.proposition_id.id})
                    print "DEBUG - Creating new proposition - id : ",prop_id
                    self.pool.get('dm.campaign.proposition.segment').write(cr, uid, wrkitem.segment_id.id, {'proposition_id':prop_id})
                    re_step_id = self.pool.get('dm.offer.step').search(cr,uid,[('offer_id','=',step.offer_id.id),('flow_start','=',True),('media_id','=',step.media_id.id)])
                    self.write(cr,uid,wrkitem.id,{'step_id':re_step_id[0]}) 
                else :
                    print "DEBUG - Updating workitem for segment"
                    self.write(cr,uid,wrkitem.id,{'step_id':trans.step_to.id})
        """
        return True

dm_offer_step_workitem()


class dm_step_product(osv.osv):
    _name = "dm.step.product"

    def _step_type(self, cr, uid, ids, name, args, context={}):
        result={}
        for id in ids:
            result[id] = self.browse(cr, uid, id).offer_step_id.type
            print "DM - result[id]",result[id]
        return result

    _rec_name = 'product_id'
    _columns = {
        'product_id' : fields.many2one('product.product', 'Product', required=True, context={'flag':True}),
        'offer_step_id': fields.many2one('dm.offer.step', 'Offer Step'),
        'offer_step_type': fields.function(_step_type,string='Offer Step Type',type="char",method=True,readonly=True), 
        'item_type': fields.selection(AVAILABLE_ITEM_TYPES, 'Item Type', size=64),
        'notes' : fields.text('Notes'),
        'purchase_constraints' : fields.text('Purchase Constraints'),
    }
dm_step_product()


class dm_product(osv.osv):
    _name = "dm.product"
    _rec_name = 'product_id'
    _columns = {
        'product_id' : fields.many2one('product.product', 'Product', required=True, context={'flag':True}),
        'qty_planned' : fields.integer('Planned Quantity'),
        'qty_real' : fields.integer('Real Quantity'),
        'price' : fields.float('Sale Price'),
        'proposition_id': fields.many2one('dm.campaign.proposition', 'Commercial Proposition'),
        'item_type': fields.selection(AVAILABLE_ITEM_TYPES, 'Item Type', size=64),
        'offer_step_type': fields.char(string='Offer Step Type',type="char",size=64), 
        'notes' : fields.text('Notes'),
    }
dm_product()

class dm_offer_step_manufacturing_constaint(osv.osv):
    _name = "dm.offer.step.manufacturing_constraint"
    _columns = {
        'name': fields.char('Description', size=64, required=True),
        'country_ids': fields.many2many('res.country','dm_manuf_constraint_country_rel','manuf_constraint_id','country_id','Country'),
        'constraint': fields.text('Manufacturing Description'),
        'offer_step_id': fields.many2one('dm.offer.step', 'Offer Step'),
    }
dm_offer_step_manufacturing_constaint()


class product_product(osv.osv):
    _name = "product.product"
    _inherit = "product.product"

    def fields_view_get(self, cr, user, view_id=None, view_type='form', context=None, toolbar=False):
        result=super(product_product,self).fields_view_get(cr, user, view_id, view_type, context, toolbar)
        if 'flag' in context:
            if result['type']=='form':
                for k,v in result['fields'].items():
                    if not (k=='name' or k=='default_code' or k=='categ_id' or k=='list_price' or k=='standard_price' or k=='seller_ids' \
                        or k=='description' or k=='description_sale'  or k=='description_purchase'):
                        del result['fields'][k]

                result['arch']= """<?xml version="1.0" encoding="utf-8"?>\n<form string="Product">\n<notebook>\n<page string="General">\n<field name="name" select="1"/>\n<field name="default_code" select="1"/>\n<field name="categ_id" select="1"/>\n<field name="list_price"/>\n<field name="standard_price"/>\n<field colspan="4" name="seller_ids" nolabel="1" widget="one2many_list"/>\n</page>\n
                    <page string="Descriptions">\n<separator string="Description" colspan="4"/>\n<field colspan="4" name="description" nolabel="1"/>\n<separator string="Sale Description" colspan="4"/>\n
                    <field colspan="4" name="description_sale" nolabel="1"/>\n<separator string="Purchase Description" colspan="4"/>\n<field colspan="4" name="description_purchase" nolabel="1"/>\n</page>\n</notebook>\n</form>"""
        return result

product_product()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

