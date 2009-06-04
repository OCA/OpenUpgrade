import time
import ir
from osv import osv,fields
import base64
import netsvc

class tinythunderbird_partner(osv.osv):

    def _links_get(self, cr, uid, context={}):
        obj = self.pool.get('res.request.link')
        ids = obj.search(cr, uid, [])
        res = obj.read(cr, uid, ids, ['object', 'name'], context)

        return [(r['object'], r['name']) for r in res]

    _name = "tinythunderbird.partner"
    _description="Thunderbid mails"
    _rec_name="sender"
    _columns = {
                'sender':fields.char("Sender",size=128,required=True,select=True),
                'receiver':fields.text("Receiver"),
                "copy_to":fields.text("Copy To"),
                "date":fields.date("Date",select=True),
                "title":fields.char("Subject",size=128,select=True),
                "description":fields.text("Description"),
                "reference":fields.reference("Reference", selection=_links_get, size=128),
                "res_user_id":fields.many2one("res.users","User"),
                "attachments":fields.text("Attached Files",readonly=True),
                }
    _defaults = {
                 'res_user_id':lambda obj,cr,uid,context: uid,
                 'date': lambda *a: time.strftime('%Y-%m-%d')
                 }

    def thunderbird_mailcreate(self,cr,user,vals):
        dictcreate = dict(vals)
        add_obj=self.pool.get('res.partner.address')
        case_pool=self.pool.get('crm.case')
        partner_ids=add_obj.search(cr,user,[('email','=',dictcreate['email_from'])])
        partner=add_obj.read(cr,user,partner_ids,['partner_id'])
        if partner:
            dictcreate.update({'partner_id':partner[0]['partner_id'][0]})
        search_id = self.pool.get('res.request.link').search(cr,user,[('object','=',dictcreate['ref'].split(',')[0])])
        if not search_id:
            create_link_id = self.pool.get('res.request.link').create(cr,user,{'name':dictcreate['ref'].split(',')[0],'object':dictcreate['ref'].split(',')[0]})
        create_id = self.pool.get('crm.case').create(cr, user, dictcreate)
        cases=case_pool.browse(cr,user,[create_id])
        case_pool._history(cr, user, cases, _('Archive'), history=True, email=False)
        return create_id
#    def thunderbird_mailcreate(self,cr,user,vals):
#        print vals
#        dictcreate = dict(vals)
#        print vals
#        domain = [('name','ilike','Thunderbird%'),('type','=','ir.actions.act_window'),('res_model','=','tinythunderbird.partner'),('src_model','=',dictcreate['reference'].split(',')[0])]
#        act_window_obj = self.pool.get('ir.actions.act_window')
#        ir_values_obj = self.pool.get('ir.values')
#        ir_model_data_obj = self.pool.get('ir.model.data')
#        if not act_window_obj.search(cr,user,domain):
#            act_window_id = act_window_obj.create(cr,user,{'name':'Thunderbird Mails','type':'ir.actions.act_window','res_model':'tinythunderbird.partner','src_model':dictcreate['reference'].split(',')[0],'domain':"[('reference', '=','" + dictcreate['reference'].split(',')[0] + ",%d'%active_id)]"})
#            ir_values_id = ir_values_obj.create(cr,user,{'name':'tinythunderbird','key':'action','model':dictcreate['reference'].split(',')[0],'key2':'client_action_relate','object':True,'value':'ir.actions.act_window,'+str(act_window_id)})
#            ir_model_data_id = ir_model_data_obj.create(cr,user,{'res_id':act_window_id,'name':'tinythunderbird','module':'thunderbird_interface','model':'ir.actions.act_window'})
#        search_id = self.pool.get('res.request.link').search(cr,user,[('object','=',dictcreate['reference'].split(',')[0])])
#        if not search_id:
#            create_link_id = self.pool.get('res.request.link').create(cr,user,{'name':dictcreate['reference'].split(',')[0],'object':dictcreate['reference'].split(',')[0]})
#        create_id = self.pool.get('tinythunderbird.partner').create(cr, user, dictcreate)
#        return create_id

    def thunderbird_createcontact(self,cr,user,vals):
        dictcreate = dict(vals)
        create_id = self.pool.get('res.partner.address').create(cr, user, dictcreate)
        return create_id

    def thunderbird_createpartner(self,cr,user,vals):
        dictcreate = dict(vals)
        search_id = self.pool.get('res.partner').search(cr, user,[('name','=',dictcreate['name'])])
        if search_id:
            return 0
        create_id = self.pool.get('res.partner').create(cr, user, dictcreate)
        return create_id

    def thunderbird_searchobject(self,cr,user,vals):
        dictcreate = dict(vals)
        search_id = self.pool.get('ir.model').search(cr, user,[('model','=',dictcreate['model'])])
        return (search_id and search_id[0]) or 0

    def thunderbird_searchcontact(self,cr,user,vals):
        search_id1 = self.pool.get('res.partner.address').search(cr,user,[('name','ilike',vals)])
        search_id2 = self.pool.get('res.partner.address').search(cr,user,[('email','=',vals)])
        if search_id1:
            return self.pool.get('res.partner.address').name_get(cr, user, search_id1)
        elif search_id2:
            return self.pool.get('res.partner.address').name_get(cr, user, search_id2)
        return []

    def thunderbird_tempsearch(self,cr,user,vals):
        if vals[0]:
            value = vals[0][0]
        if vals[1]:
            obj = vals[1];
        name_get=[]
        er_val=[]
        for object in obj:
            if object == 'res.partner.address':
                search_id1 = self.pool.get(object).search(cr,user,[('name','ilike',value)])
                search_id2 = self.pool.get(object).search(cr,user,[('email','=',value)])
                if search_id1:
                    name_get.append(object)
                    name_get.append(self.pool.get(object).name_get(cr, user, search_id1))
                elif search_id2:
                    name_get.append(object)
                    name_get.append(self.pool.get(object).name_get(cr, user, search_id2))
            else:
                try:
                    search_id1 = self.pool.get(object).search(cr,user,[('name','ilike',value)])
                    if search_id1:
                        name_get.append(object)
                        name_get.append(self.pool.get(object).name_get(cr, user, search_id1))
                except:
                    er_val.append(object)
                    continue
        if len(er_val) > 0:
            name_get.append('error')
            name_get.append(er_val)
        
        return name_get

    def thunderbird_attachment(self,cr,user,vals):
        dictcreate = dict(vals)
        datas = [dictcreate['datas']]
        name = [dictcreate['name']]
        if(dictcreate['datas'].__contains__(',')):
            name = dictcreate['name'].split(',')
            datas = dictcreate['datas'].split(',')
        for i in range(0,datas.__len__()):
            dictcreate['name'] = name[i]
            dictcreate['datas'] = datas[i]
            create_id = self.pool.get('ir.attachment').create(cr,user,dictcreate)
        return 0

    def thunderbird_login(self,cr,user,vals):
        dictcreate = dict(vals)
        service = netsvc.LocalService('common')
        res = service.login(dictcreate['db'],dictcreate['login'],dictcreate['passwd'])
        return res or 0

    def read(self, cr, user, ids, fields=None, context={}, load='_classic_read'):
         ret_read = super(tinythunderbird_partner, self).read(cr, user, ids,fields,context,load)
         for read_data in ret_read:
             attachments = self.pool.get('ir.attachment').search(cr,user,[('res_model','=',self._name),('res_id','=',read_data['id'])])
             attechments_data = self.pool.get('ir.attachment').read(cr,user,attachments,['name'])
             file_names = [a['name'] for a in attechments_data]
             text_atteched = '\n'.join(file_names)
             read_data['attachments'] = text_atteched
         return ret_read

    def unlink(self, cr, uid, ids, context={}):
        attachments = self.pool.get('ir.attachment').search(cr,uid,[('res_model','=',self._name),('res_id','in',ids)])
        self.pool.get('ir.attachment').unlink(cr,uid,attachments)
        return super(tinythunderbird_partner, self).unlink(cr, uid, ids,context)

tinythunderbird_partner()