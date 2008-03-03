import time
import netsvc
from osv import fields, osv
import ir
from mx import DateTime
from tools import config

class ir_translation_contribution(osv.osv):
    _name = "ir.translation.contribution"
    _inherits = {'ir.translation': 'translation_id'}
    _description = "Translation Contribution"
    _columns = {
            'translation_id' : fields.many2one('ir.translation','Original Transaltion'),
            'contributor_email'  : fields.char('Email Id of Contibutor',size=128),      
            'state': fields.selection(
                    [('draft','Draft'),
                     ('propose','Propose for Change'),
                     ('unchange',"Don't change"),
                     ('accpet','Accept'),
                     ('deny','Deny'),
                     ('done','Done'),],
                     'Translation State', readonly=True, select=True), 
                }   
    
#    _sql = """
#        create index ir_translation_ltn1 on ir_translation (lang,type,name);
#        create index ir_translation_res_id1 on ir_translation (res_id);
#    """
    
ir_translation_contribution()