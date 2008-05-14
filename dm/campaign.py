import time
import offer
from osv import fields
from osv import osv

print dir(offer)

class dm_campaign(osv.osv):
    _name = "dm.campaign"
    _inherit = "account.analytic.account"
    _rec_name = 'name'
    def pao_making_time_get(self, cr, uid, ids, name, arg, context={}):
        return name
    
    _columns = {
        'name' : fields.char('Campaign', size=64),
        'offer_id' : fields.many2one('dm.offer', 'Offer'),
        'country_id' : fields.many2one('res.country', 'Country'),
        'lang_id' : fields.many2one('res.lang', 'Language'),
        'state' : fields.selection([('planning','Planning'), ('open','Open'), ('fabrication','Fabrication'), ('close','Close'), ('cancel','Cancel')], 'State'),
        'partner_id' : fields.many2one('res.partner', 'Associated partner', help="TO CHANGE : check donneur d'ordre"),
        'trademark_id' : fields.many2one('dm.trademark', 'Trademark', help="TO CHECK : trademark"),
#        'receiver_id' fields.many2one(' ','Receiver'),
        'project_id' : fields.many2one('project.project', 'Project Retroplanning', required=True),
        'campaign_stat_ids' : fields.one2many('dm.campaign.statistics','camp_id','Statistics'),
        'product_ids' : fields.one2many('dm.campaign.product', 'product_id', 'Products'),
        'proposition_ids' : fields.one2many('dm.campaign.proposition', 'name', 'Proposition'),
        'pao_making_time' : fields.function(pao_making_time_get, method=True, type='float', string='Making Time')
                }
 
dm_campaign()

class dm_campaign_statistics(osv.osv):
    _name = "dm.campaign.statistics"
    _columns = {
        'kind' : fields.char('Kind', size=16),
        'qty' : fields.integer('Quantity'),
        'rate' : fields.float('Rate', digits=(16,2)),
        'camp_id' : fields.many2one('dm.campaign', 'Campaign')
                }

dm_campaign_statistics()

class dm_campaign_product(osv.osv):
    _name = "dm.campaign.product"
    _columns = {
        'product_id' : fields.many2one('product.product', 'Product'),
        'qty_planned' : fields.integer('Planned Quantity'),
        'qty_real' : fields.float('Real Quantity'),
        'price' : fields.float('Sale Price')
                }
    
dm_campaign_product()

class dm_campaign_proposition(osv.osv):
    _name = "dm.campaign.proposition"
    _columns = {
        'name' : fields.char('Name', size=64),
        'delay_ids' : fields.one2many('dm.campaign.delay', 'proposition_id', 'Delays')
                }
    
dm_campaign_proposition()

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
        'name' : fields.char('Name', size=64),
        'campaign_ids' : fields.one2many('dm.campaign', 'name' , 'Campaigns')
                }
    
dm_campaign_group()