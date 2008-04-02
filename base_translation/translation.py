import time
import netsvc
from osv import fields, osv
import ir
from mx import DateTime
import tools 
import xmlrpclib
import pooler

from wizard import SERVER,PORT
s = xmlrpclib.Server("http://"+SERVER+":"+str(PORT))

def get_version(cr, uid,context):
    user = pooler.get_pool(cr.dbname).get('res.users').read(cr,uid,uid,['login'])['login']
    return s.version_list(user)
    
def get_profile(cr,uid,context):
    user = pooler.get_pool(cr.dbname).get('res.users').read(cr,uid,uid,['login'])['login']
    return s.profile_list(user)

def get_language(cr,uid,context,user=None,model=None,lang=None):
    if user:
        if user=='contributor':
            list = s.get_lang_list()
        else:
            login = pooler.get_pool(cr.dbname).get('res.users').read(cr,uid,uid,['login'])['login']
            list = s.get_lang_list(login)
    elif model:
        if model=='ir_translation_contrib':
            sql = "select distinct lang from ir_translation_contribution where state='propose'"
        else:
            sql = "select distinct lang from ir_translation"
        cr.execute(sql)
        list = map(lambda x: x[0],cr.fetchall())
    else :
        sql = "select distinct lang from ir_translation_contribution where state='accept'"
        cr.execute(sql)
        list = map(lambda x: x[0],cr.fetchall())        
    lang_dict = tools.get_languages()
    return [(lang, lang_dict.get(lang, lang)) for lang in list]

#
#class ir_translation(osv.osv):
#    _inherit = 'ir.translation'
#    _columns = {
#                'version':fields.char('Version',size=64),
#                'profile':fields.char('profile',size=64),
#            }
#ir_translation()

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
                     ('accept','Accept'),
                     ('done','Done'),                     
                     ('deny','Deny'),
                     ],
                     'Translation State', readonly=True, select=True),
#            so same contribution doesnt upload more than once
            'upload':fields.boolean('upload') 
                }
    _sql = ''    

    def write(self, cr, uid, ids, vals, context=None):
        if self.read(cr,uid,ids,['upload']):
            vals['upload']=False
        return super(ir_translation_contribution, self).write(cr, uid, ids, vals, context=context)

ir_translation_contribution()