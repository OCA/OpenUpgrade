import time
import offer

from osv import fields
from osv import osv


class dm_campaign(osv.osv):
    _name = "dm.campaign"
    _inherits = {'account.analytic.account': 'analytic_account_id'}
    _rec_name = 'name'

    def dtp_making_time_get(self, cr, uid, ids, name, arg, context={}):
        
        return name
    
    _columns = {
        'offer_id' : fields.many2one('dm.offer', 'Offer'),
        'country_id' : fields.many2one('res.country', 'Country'),
        'lang_id' : fields.many2one('res.lang', 'Language'),
        'trademark_id' : fields.many2one('dm.trademark', 'Trademark', help="TO CHECK : trademark"),
        'project_id' : fields.many2one('project.project', 'Project', readonly=True),
        'notes' : fields.text('Notes'),
        'campaign_stat_ids' : fields.one2many('dm.campaign.statistics','camp_id','Statistics'),
        'proposition_ids' : fields.one2many('dm.campaign.proposition', 'camp_id', 'Proposition'),
        'campaign_type' : fields.selection([('view','View'),('general','General'),('production','Production'),('purchase','Purchase')],"Type"),
        'analytic_account_id' : fields.many2one('account.analytic.account','Analytic Account', ondelete='cascade'),
        'planning_state' : fields.selection([('pending','Pending'),('inprogress','In Progress'),('done','Done')], 'Planning Status'),
        'manufacturing_state' : fields.selection([('pending','Pending'),('inprogress','In Progress'),('done','Done')], 'Manufacturing Status'),
#  
#                        desktop publication
#  
        'dtp_date_delivery' : fields.date('Delivery Date'),
        'dtp_date_real_delivery' : fields.date('Real Delivery Date'),
        'dtp_intervention_type' : fields.date('Intervention Date'),
        'dtp_making' : fields.char('Making',size=64),    
        'dtp_operator' : fields.many2one('res.partner','Operator'),
        'dtp_date_recovered' : fields.date('Recovered Date'),
        'dtp_notes' : fields.text('Notes'),            
        'responsible_id' : fields.many2one('res.users','Responsible'),
#        'campaign_partner_id' : fields.many2one('res.partner', 'Associated partner', help="TO CHANGE : check donneur d'ordre"),
        'dtp_making_time' : fields.function(dtp_making_time_get, method=True, type='float', string='Making Time'),
    }
    
    _defaults = {
        'state': lambda *a: 'draft',
        'planning_state': lambda *a: 'pending',
        'manufacturing_state': lambda *a: 'pending',
        'campaign_type': lambda *a: 'general',
    }

    def onchange_offer(self, cr, uid, ids, offer_id):
        value={'name':''}
        if not offer_id:
            return {'value':value}
        res = self.pool.get('dm.offer').browse(cr,uid,[offer_id])[0]
        value['name']=res.name
        return {'value':value}

    def state_draft_set(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'draft'})
        return True  

    def state_close_set(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'close'})
        return True  

    def state_pending_set(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'pending'})
        return True

    def state_open_set(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'open'})
        return True 
dm_campaign()

#Postgres view
class dm_campaign_statistics(osv.osv):
    _name = "dm.campaign.statistics"
    _columns = {
        'kind' : fields.char('Kind', size=16),
        'qty' : fields.integer('Quantity'),
        'rate' : fields.float('Rate', digits=(16,2)),
        'camp_id' : fields.many2one('dm.campaign', 'Campaign')
    }
dm_campaign_statistics()


#class dm_campaign_pricelist(osv.osv):
#    _name = "dm.campaign.pricelist"
#    _description = "Pricelist"
#    _columns = {
#        'name': fields.char('Name',size=64, required=True),
#        'active': fields.boolean('Active'),
#        'type': fields.selection([('customer','Customer'),('requirer','Requirer')], 'Pricelist Type', required=True),
#        'currency_id': fields.many2one('res.currency', 'Currency', required=True),
#    }
#
#    _defaults = {
#        'active': lambda *a: 1,
#    }
#dm_campaign_pricelist()

class dm_campaign_proposition(osv.osv):
    _name = "dm.campaign.proposition"
    _inherits = {'account.analytic.account': 'analytic_account_id'}
    _columns = {
        'camp_id' : fields.many2one('dm.campaign','Campaign',ondelete = 'cascade',required=True),
        'delay_ids' : fields.one2many('dm.campaign.delay', 'proposition_id', 'Delays', ondelete='cascade'),
        'sale_rate' : fields.float('Sale Rate', digits=(16,2)),
        'proposition_type' : fields.selection([('init','Init'),('recall','Recall')],"Type"),
        'segment_ids' : fields.one2many('dm.campaign.proposition.segment','proposition_id','Segment', ondelete='cascade'),        
        'customer_pricelist_id':fields.many2one('product.pricelist','Customer Pricelist'),
        'requirer_pricelist_id' : fields.many2one('product.pricelist','Requirer Pricelist'),
        'notes':fields.text('Notes'),
        'analytic_account_id' : fields.many2one('account.analytic.account','Analytic Account', ondelete='cascade'),
    }
    
    _defaults = {
        'proposition_type' : lambda*a : 'general',
    }
    

    def _check(self, cr, uid, ids=False, context={}):
        '''
        Function called by the sceduler to create workitem from the segments of propositions.
        '''
        ids = self.search(cr,uid,[('date_start','=',time.strftime('%Y-%m-%d %H:%M:%S'))])
        for id in ids:
            res = self.browse(cr,uid,[id])[0]
            offer_step_id = self.pool.get('dm.offer.step').search(cr,uid,[('offer_id','=',res.camp_id.offer_id.id),('flow_start','=',True)])
            if offer_step_id : 
                vals = {'step_id':offer_step_id[0],'segment_id':id}
                new_id = self.pool.get('dm.offer.step.workitem').create(cr,uid,vals)
        return True
    
dm_campaign_proposition()

class dm_campaign_proposition_segment(osv.osv):
    
    _name = "dm.campaign.proposition.segment"
    _inherits = {'account.analytic.account': 'analytic_account_id'}
    _description = "Segment"
    _columns = {
        'action_code': fields.char('Code',size=16, required=True),
        'proposition_id' : fields.many2one('dm.campaign.proposition','Proposition', required=True, ondelete='cascade'),
        'qty': fields.integer('Qty'),
        'analytic_account_id' : fields.many2one('account.analytic.account','Analytic Account', ondelete='cascade'),
        'note' : fields.text('Notes'),
        'sequence' : fields.integer('Sequence'),
    }
    _order = 'sequence'
    
dm_campaign_proposition_segment()

class dm_campaign_delay(osv.osv):
    _name = "dm.campaign.delay"
    _columns = {
        'key_id' : fields.many2one('dm.offer.delay', 'Offer delay'),
        'value' : fields.integer('Value'),
        'proposition_id' : fields.many2one('dm.campaign.proposition', 'Proposition')
    }
    
dm_campaign_delay()

class dm_campaign_group(osv.osv):
    _name = "dm.campaign.group"
    _columns = {
        'name' : fields.char('Name', size=64, required=True),
        'campaign_ids': fields.many2many('dm.campaign', 'dm_campaign_group_rel', 'group_id', 'campaign_id', 'Campaigns')
    }
    
dm_campaign_group()
