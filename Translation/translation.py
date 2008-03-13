import time
import netsvc
from osv import fields, osv
import ir
from mx import DateTime
import tools 
import xmlrpclib
s = xmlrpclib.Server("http://192.168.0.4:8000")

def get_language(cr,uid,context,user=None,model=None):
    if user:
        if user=='contributor':
            file_list = s.get_publish_list()
            print file_list
        else:
            file_list = s.get_contrib_list()
        list = map(lambda x: x.replace('.csv',''),file_list)
    else:
        sql = "select distinct lang from %s"%model
        cr.execute(sql)
        list = map(lambda x: x[0],cr.fetchall())
    lang_dict = tools.get_languages()
    print "list :",list
    return [(lang, lang_dict.get(lang, lang)) for lang in list]

class ir_translation_contribution(osv.osv):
    _name = "ir.translation.contribution"
    _inherit = 'ir.translation'
    _description = "Translation Contribution"
    _columns = {
            'contributor_email'  : fields.char('Email Id of Contibutor',size=128),      
            'state': fields.selection(
                    [('draft','Draft'),
                     ('propose','Propose for Change'),
                     ('unchange',"Don't change"),
                     ('done','Accept'),
                     ('deny','Deny'),
                     ],
                     'Translation State', readonly=True, select=True),
            'upload':fields.boolean('upload') 
                }
    
    _sql = """
        create index ir_translation_ltn1 on ir_translation (lang,type,name);
        create index ir_translation_res_id1 on ir_translation (res_id);
    """

ir_translation_contribution()