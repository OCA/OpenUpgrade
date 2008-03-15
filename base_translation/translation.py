import time
import netsvc
from osv import fields, osv
import ir
from mx import DateTime
import tools 
import xmlrpclib
import pooler
s = xmlrpclib.Server("http://192.168.0.4:8000")

def get_language(cr,uid,context,user=None,model=None):
    if user:
        if user=='contributor':
            file_list = s.get_publish_list()
        else:
            login = pooler.get_pool(cr.dbname).get('res.users').read(cr,uid,uid,['login'])['login']
            if user=='maintainer_publish':
                user_list = s.get_publish_list(login)
                cr.execute("select distinct(lang) from ir_translation_contribution where state='accept'")
                db_lang_list =map(lambda x: x[0],cr.fetchall())
                file_list = filter(lambda x:x in user_list,db_lang_list)
            else:
                
#                code should be optimise

                file_list = s.get_contrib_list(login)
                lang_list=[]
                lang_dict = tools.get_languages()
                for f in file_list:
                    if f.find('AT')>0:
                        splited_name = f.split('-')
                        name = splited_name[1].split('_AT')[0]
                        vn = splited_name[-1].replace('.csv','')
                        lang_name = lang_dict.get(splited_name[0],splited_name[0])
                        lang_list.append((f,lang_name+' by '+name+' V'+vn))
                    else :
                        f = f.replace('.csv','')
                        lang_list.append((f, lang_dict.get(f,f)))
                return lang_list
        list = map(lambda x: x.replace('.csv',''),file_list)
    else:
        sql = "select distinct lang from %s"%model
        cr.execute(sql)
        list = map(lambda x: x[0],cr.fetchall())
    lang_dict = tools.get_languages()
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
                     ('accept','Accept'),
                     ('done','Done'),                     
                     ('deny','Deny'),
                     ],
                     'Translation State', readonly=True, select=True),
#            so same contribution doesnt upload more than once
            'upload':fields.boolean('upload') 
                }
    
    _sql = ''    
#    _sql = """
#        create index ir_translation_ltn1 on ir_translation (lang,type,name);
#        create index ir_translation_res_id1 on ir_translation (res_id);
#    """
    def write(self, cr, uid, ids, vals, context=None):
        if self.read(cr,uid,ids,['upload']):
            vals['upload']=False
        return super(ir_translation_contribution, self).write(cr, uid, ids, vals, context=context)

ir_translation_contribution()