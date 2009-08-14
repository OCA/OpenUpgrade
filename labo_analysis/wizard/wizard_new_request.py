##############################################################################
#
# Copyright (c) 2004 TINY SPRL. (http://tiny.be) All Rights Reserved.
#  Fabien Pinckaers <fp@tiny.Be>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import wizard
from osv import fields, osv
import pooler
take_fields = {
}
take_form = """<?xml version="1.0"?>
<form string="Create request for ko analysis">
     <separator string="Create new request" colspan="4"/>
     <newline/>
</form>
"""

in_form = '''<?xml version="1.0"?>
<form string="Set number to the request ?">
    <field name="number"/>
</form>'''
in_fields = {
    'number': {'string':'Request Number', 'type':'char','required':'True'},

}


def _new(self, cr, uid, data, context):
    refs = pooler.get_pool(cr.dbname).get('labo.analysis.request')
    rec_ids = refs.browse(cr,uid,data['ids'])
    req_obj = pooler.get_pool(cr.dbname).get('labo.sample')
    dog_obj = pooler.get_pool(cr.dbname).get('labo.dog')
    req_follow = pooler.get_pool(cr.dbname).get('labo.followsheet')
    ref_hist=pooler.get_pool(cr.dbname).get('sample.history')
    res1=[]
    a=[]
    view_type=''
    for rec in rec_ids:
        view_type=rec.type_id.code
        if rec.type_id.code=="EMPDOG" or rec.type_id.code=="EMPDOG_2" or rec.type_id.code=="EMPCHE":
            cr.execute("SELECT s.id,r.id from labo_dog d ,labo_analysis_request r, labo_sample s where s.sample_id=r.id and r.id=%d  and (s.dog_mother=d.id or s.dog_father=d.id or s.dog_child=d.id) and d.nc_reanalyse='t'"%(rec.id))
            res=cr.fetchall()
            for r in res:
                res1.append(r[0])
            #res1=",".join([str(x[0]) for x in res1 if x])
        else:
            res1=req_obj.search(cr,uid,[('nc_reanalyse','=',True),('sample_id','in',data['ids'])])
        res=req_obj.browse(cr,uid,res1)

        if not res1:
            raise wizard.except_wizard('Error!', 'No Samples to reanalyse')
        new_id=refs.create(cr,uid,{
                'ref_client': rec.ref_client.id,
                'type_id':rec.type_id.id,
                'pricelist_id':False,
                'name':data['form']['number'],
                })
        id_req=refs.search(cr,uid, [('name','=',data['form']['number'])])
        for r in res:
            if rec.type_id.code!="EMPDOG" or rec.type_id.code!="EMPDOG_2" or rec.type_id.code!="EMPCHE" :
                req_id=r.sample_id
            hist_id=ref_hist.create(cr,uid,{'request_id':rec.id,
                                        'req_id':new_id,
                                        'sample_id': r.id
                                        })

            hist_id1=ref_hist.create(cr,uid,{'req_id': new_id,
#                                        'request_id': rec.name,
                                        'request_id':rec.id,
                                        'sample_id': r.id
                                        })
            new_hist=req_obj.create(cr,uid, {'history_ids': [(4,hist_id)]})
        #    new_hist=req_obj.write(cr,uid, [r.id], {'history_ids': [(4,hist_id)]})
        #    hist_id=ref_hist.create(cr,uid,{'req_id':new_id,
        #                                    'request_id': rec.name,
        #                                    'sample_id':new_id
        #                                    })
            if view_type!='EMPDOG' and view_type!='EMPDOG_2' and view_type!='EMPCHE' :
                new_hist1=req_obj.create(cr,uid, {'history_ids': [(4,hist_id)],
                                                'sample_id': new_id,
                                                'sanitel': r.sanitel,
                                                'progenus_number': r.progenus_number,
                                                'code': r.code,
#                                                'follow_sheet_id': r.follow_sheet_id,
                                                'material': r.material
                                            })
            elif rec.type_id.code=='EMPDOG':
                new_hist1=req_obj.create(cr,uid, {'history_ids': [(4,hist_id)],
                                                'sample_id': new_id,
                                                'dog_mother': r.dog_mother.id or None,
                                                'dog_child':r.dog_child.id or None,
                                                'dog_father':r.dog_father.id or None,
                                                'date_reception':r.date_reception,
                                                'preleveur1_id':r.preleveur1_id.id or None,
                                                'lp_file':r.lp_file or None,
                                                'lp_doss':r.lp_doss or None,
                                                'lp_serv':r.lp_serv or None,
                                                'res_filiation':'',
                                                'date_closing':r.date_closing or None,
                                                'date_limit':r.date_limit or None,
                                            })    
            elif rec.type_id.code=='EMPDOG_2':
                new_hist1=req_obj.create(cr,uid, {'history_ids': [(4,hist_id)],
                                                'sample_id': new_id,
                                                'dog_mother': r.dog_mother.id or None,
                                                'dog_father':r.dog_father.id or None,
                                                'date_reception':r.date_reception,
                                                'preleveur1_id':r.preleveur1_id.id or None,
                                                'lp_file':r.lp_file or None,
                                                'lp_doss':r.lp_doss or None,
                                                'lp_serv':r.lp_serv or None,
                                                'res_filiation':'',
                                                'date_closing':r.date_closing or None,
                                                'date_limit':r.date_limit or None,
                                                   })    

    return {}


def create_case_sample(self, cr, uid, data, context):
    ref_case = pooler.get_pool(cr.dbname).get('crm.case')
    sample_obj = pooler.get_pool(cr.dbname).get('labo.sample')
    req_obj = pooler.get_pool(cr.dbname).get('labo.analysis.request')
    dog_obj = pooler.get_pool(cr.dbname).get('labo.dog')
    rec_ids = sample_obj.browse(cr,uid,data['ids'])
    view_b=sample_obj.browse(cr,uid,data['ids'])[0]
    view_type=view_b.cont
    list_sample=[]
    if not view_type:
        view_type=view_b.sample_id.type_id.code
    v_lines=[]
    res_nc1=dog_obj.search(cr,uid,[('nc_reanalyse','=',True)])
    section_id=pooler.get_pool(cr.dbname).get('crm.case.section').search(cr, uid,[('name', '=', 'Analysis'),])
    section_id1=pooler.get_pool(cr.dbname).get('crm.case.section').search(cr, uid,[('name', '=', 'NC Reanalyse'),])
    section_id2=pooler.get_pool(cr.dbname).get('crm.case.section').search(cr, uid,[('name', '=', 'NC Finale'),])
    ids_new=[]
    for req in rec_ids:
        cr.execute("SELECT d.progenus_number,s.id from labo_dog d , labo_sample s where s.id =%d and (s.dog_mother=d.id or s.dog_father=d.id "\
                    "or s.dog_child=d.id) and d.nc_reanalyse='t'"%(req.id))
        res1=cr.fetchall()
        res_nc=",".join([str(x[0]) for x in res1 if x[0]])

        cr.execute("SELECT d.progenus_number,s.id from labo_dog d , labo_sample s where s.id=%d and (s.dog_mother=d.id or s.dog_father=d.id or "\
                    "s.dog_child=d.id) and d.nc_gle='t'"%(req.id))
        res2=cr.fetchall()
        res_gl=",".join([str(x[0]) for x in res2 if x[0]]) 

        cr.execute("SELECT d.progenus_number from labo_dog d , labo_sample s where s.id =%d and (s.dog_mother=d.id or s.dog_father=d.id or "\
                    "s.dog_child=d.id) and d.date_closing>d.date_limit"%(req.id))
        res3=cr.fetchall()
        res_dl=",".join([str(x[0]) for x in res3 if x[0]])

        cr.execute("SELECT d.progenus_number,s.id from labo_dog d , labo_sample s where s.id=%d and (s.dog_mother=d.id or s.dog_father=d.id or "\
                    "s.dog_child=d.id) and d.final_c='t'"%(req.id))
        res4=cr.fetchall()
        res_final=",".join([str(x[0]) for x in res4 if x[0]]) 
        ## FIND LABO DOG WITH NC
      #  record = sample_obj.browse(cr,uid,res_nc)
#        section_id_date=pooler.get_pool(cr.dbname).get('crm.case.section').search(cr, uid,[('name', '=', 'NC Date'),])
        section_id_gl=pooler.get_pool(cr.dbname).get('crm.case.section').search(cr, uid,[('name', '=', 'NC Gl'),])
        txt_mail="We urge you to send us other samples, corresponding to the following progenus number or certification numbers :"+'\n'
        li=[]
        new_id_nc_r=0
        new_id2=0
        new_id_date=0
        #If date_limit of sample is > date_closing of request => create a case in the section analysis
        if res_dl:
            new_id_date=ref_case.create(cr,uid,{
                'name': "CASE LIMIT DATE " + res_dl,
                'section_id':section_id[0],
                'partner_id':req.preleveur1_id.id,
            #    'partner_id':req.user_id.company_id.partner_id.id,
                'state': 'open',
                'active':True,
                'description': "NC Date limit: "+"  "+txt_mail+ res_dl
            })

        if res_nc:
            email_from=req.preleveur1_id and req.preleveur1_id.address and req.preleveur1_id.address[0].email or ''
            new_id_nc_r=ref_case.create(cr,uid,{
                'name': "CASE NC REANALYSE " + res_nc,
                'section_id':section_id1[0],
                'partner_id':req.preleveur1_id.id,
                'email_from':email_from,
                'partner_address_id':req.preleveur1_id and req.preleveur1_id.address and req.preleveur1_id.address[0].id,
                'state': 'open',
                'active':True,
                'description': "NC REANALYSE: "+"  "+txt_mail+ res_nc
                })

        #If nc_general  of sample is set to True => create a case in the section analysis
        if res_gl:
            email_from=req.preleveur1_id and req.preleveur1_id.address and req.preleveur1_id.address[0].email or ''
            new_id2=ref_case.create(cr,uid,{
                'name': "CASE NC GENERAL " + res_gl,
                'section_id':section_id_gl[0],
                'partner_id':req.preleveur1_id and req.preleveur1_id.id,
            #    'partner_id':req.user_id.company_id.partner_id.id,
                'email_from':email_from,
                'partner_address_id':req.preleveur1_id and req.preleveur1_id.address and req.preleveur1_id.address[0].id,
                'state': 'open',
                'active':True,
                'description': "NC GENERAL: "+"  "+txt_mail+ res_gl
            })
        new_final=0
        if res_final:
            email_from=req.preleveur1_id and req.preleveur1_id.address and req.preleveur1_id.address[0].email or ''
            new_final=ref_case.create(cr,uid,{
                'name': "CASE FINAL CONFORMITY " + res_final,
                'section_id':section_id2[0],
                'partner_id':req.preleveur1_id and req.preleveur1_id.id,
            #    'partner_id':req.user_id.company_id.partner_id.id,
                'email_from':email_from,
                'partner_address_id':req.preleveur1_id and req.preleveur1_id.address and req.preleveur1_id.address[0].id,
                'state': 'open',
                'active':True,
                'description': "NC FINAL CONFORMITY: "+"  "+txt_mail+ res_gl
            })
        if new_id_nc_r: ids_new.append(int(new_id_nc_r))
        if new_id2: ids_new.append(int(new_id2))
        if new_id_date: ids_new.append(int(new_id_date))
        if new_final: ids_new.append(int(new_final))

        for n in ids_new:
            req_obj.write(cr,uid,[req.sample_id.id],{'case_id':[(4,n)]
                                    })

#        a=refs.write(cr,uid,[req.id],{'case_id':new_id,})
#        a=refs.write(cr,uid,[req.id],{'case_id':new_id2,})
#        b=req.case_id.id
#    for rec in rec_ids:
#        new_id=refs.create(cr,uid,{'ref_client': rec.ref_client.id,'pricelist_id':False,'sample_ids':[(6,0,res)],})
    return {
        'domain': "[('id','in', ["+','.join(map(str,ids_new))+"])]",
        'name': 'My cases',
        'view_type': 'form',
        'view_mode': 'tree,form',
        'res_model': 'crm.case',
        'view_id': False,
        'type': 'ir.actions.act_window'
    }


def create_case(self, cr, uid, data, context):
    ref_case = pooler.get_pool(cr.dbname).get('crm.case')
    refs = pooler.get_pool(cr.dbname).get('labo.analysis.request')
    rec_ids = refs.browse(cr,uid,data['ids'])
    req_obj = pooler.get_pool(cr.dbname).get('labo.sample')

    v_lines=[]
    for req in rec_ids:
        sample_ids=req_obj.search(cr,uid,[])
        sample_record=req_obj.browse(cr,uid,sample_ids)

        res_nc=req_obj.search(cr,uid,[('nc_reanalyse','=',True),('sample_id','in',data['ids'])])
        res_cfinale=req_obj.search(cr,uid,[('final_c','=',True),('sample_id','in',data['ids'])])
        res_gl=req_obj.search(cr,uid,[('nc_gle','=',True),('sample_id','in',data['ids'])])

        record = req_obj.browse(cr,uid,res_nc)
        record_gl = req_obj.browse(cr,uid,res_gl)
        record_final = req_obj.browse(cr,uid,res_cfinale)

        ids_new=[]

        section_id=pooler.get_pool(cr.dbname).get('crm.case.section').search(cr, uid,[('name', '=', 'Analysis'),])
        section_id1=pooler.get_pool(cr.dbname).get('crm.case.section').search(cr, uid,[('name', '=', 'NC Reanalyse'),])
        section_final_id=pooler.get_pool(cr.dbname).get('crm.case.section').search(cr, uid,[('name', '=', 'NC Finale'),])
#        section_id_date=pooler.get_pool(cr.dbname).get('crm.case.section').search(cr, uid,[('name', '=', 'NC Date'),])
        section_id_gl=pooler.get_pool(cr.dbname).get('crm.case.section').search(cr, uid,[('name', '=', 'NC Gl'),])

        txt_mail="We urge you to send us other samples, corresponding to the following sanitel numbers :"+'\n'
        li=[]

        new_id_nc_r=0
        new_id2=0
        new_id_date=0
        new_id_final=''
        new_final=0
        #If date_limit of sample is > date_closing of request => create a case in the section analysis
        for i in req.sample_ids:
            if i.date_limit>req.date_closed:
                li.append(i.sanitel)

        lines= dict([(i,0) for i in li]).keys()
        cc=",".join([str(x) for x in lines if x])
        if cc:
            new_id_date=ref_case.create(cr,uid,{
                'name': "CASE " + req.name,
                'section_id':section_id[0],
                'partner_id':rec_ids[0].ref_client.id,
            #    'partner_id':req.user_id.company_id.partner_id.id,
                'state': 'open',
                'active':True,
                'description': "NC Date limit:"+"  "+txt_mail+ ",".join([str(x) for x in lines if x])
            })

#        if not req.user_id and not req.user_id :
#            raise wizard.except_wizard('Error!', 'No User associated to the analyse')

        #If nc_reanalyse  of sample is set to True => create a case in the section analysis

        if res_nc:

            for rec in record:
                v_lines.append(rec.sanitel)
                lines= dict([(i,0) for i in v_lines]).keys()
            email_from=rec_ids and rec_ids[0].ref_client and rec_ids[0].ref_client.address and rec_ids[0].ref_client.address[0].email or ''
            a=",".join([str(x) for x in lines if x])
            if a:
                new_id_nc_r=ref_case.create(cr,uid,{
                    'name': "CASE " + req.name,
                    'section_id':section_id1[0],
                    'partner_id':rec_ids[0].ref_client.id or None,
                    'email_from':email_from,
                    'partner_address_id':rec_ids and rec_ids[0].ref_client and rec_ids[0].ref_client.address and rec_ids[0].ref_client.address[0].id or None,
                #    'partner_id':req.user_id.company_id.partner_id.id,
                    'state': 'open',
                    'active':True,
                    'description': "NC REANALYSE:"+"  "+txt_mail+ ",".join([str(x) for x in lines if x])
                    })

        #If nc_general  of sample is set to True => create a case in the section analysis
        if res_gl:
            for rec in record_gl:
                v_lines.append(rec.sanitel)
                lines= dict([(i,0) for i in v_lines]).keys()
            email_from=rec_ids and rec_ids[0].ref_client and rec_ids[0].ref_client.address and rec_ids[0].ref_client.address[0].email
            a=",".join([str(x) for x in lines if x])
            if a:
                new_id2=ref_case.create(cr,uid,{
                    'name': "CASE " + (req.name or ''),
                    'section_id':section_id_gl[0] or '',
                    'partner_id':rec_ids[0].ref_client.id or None,
                #    'partner_id':req.user_id.company_id.partner_id.id,
                    'email_from':email_from or '',
                    'partner_address_id':rec_ids and rec_ids[0].ref_client and rec_ids[0].ref_client.address and rec_ids[0].ref_client.address[0].id or None,
                    'state': 'open',
                    'active':True,
                    'description': "NC GENERALE"+"  "+txt_mail+ ",".join([str(x) for x in lines if x])
                })

        if res_cfinale:

            for rec in record:
                v_lines.append(rec.sanitel)
                lines= dict([(i,0) for i in v_lines]).keys()
            email_from=rec_ids and rec_ids[0].ref_client and rec_ids[0].ref_client.address and rec_ids[0].ref_client.address[0].email or ''
            if a:
                new_id_final=ref_case.create(cr,uid,{
                    'name': "CASE " + req.name,
                    'section_id':section_final_id[0],
                    'partner_id':rec_ids[0].ref_client.id or None,
                    'email_from':email_from,
                    'partner_address_id':rec_ids and rec_ids[0].ref_client and rec_ids[0].ref_client.address and rec_ids[0].ref_client.address[0].id or None,
                #    'partner_id':req.user_id.company_id.partner_id.id,
                    'state': 'open',
                    'active':True,
                    'description': "Finale Conformity:"+"  "+txt_mail+ ",".join([str(x) for x in lines if x])
                    })
        if new_id_nc_r: ids_new.append(int(new_id_nc_r))
        if new_id2: ids_new.append(int(new_id2))
        if new_id_date: ids_new.append(int(new_id_date))
        if new_id_final: ids_new.append(int(new_id_final))


        for n in ids_new:
            refs.write(cr,uid,[req.id],{'case_id':[(4,n)]
                                    })

#        a=refs.write(cr,uid,[req.id],{'case_id':new_id,})
#        a=refs.write(cr,uid,[req.id],{'case_id':new_id2,})
#        b=req.case_id.id
#    for rec in rec_ids:
#        new_id=refs.create(cr,uid,{'ref_client': rec.ref_client.id,'pricelist_id':False,'sample_ids':[(6,0,res)],})
    return {
        'domain': "[('id','in', ["+','.join(map(str,ids_new))+"])]",
        'name': 'My cases',
        'view_type': 'form',
        'view_mode': 'tree,form',
        'res_model': 'crm.case',
        'view_id': False,
        'type': 'ir.actions.act_window'
    }

class wiz_new_req(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch' : in_form,'fields' : in_fields, 'state':[ ('end','Cancel'),('_new_req','New Request for nc samples')]}
        },
        '_new_req' : {
            'actions' : [_new],
            'result' : {'type' : 'state', 'state' : 'end'}
        },
    }
wiz_new_req("labo.new.req")



class wiz_new_case(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch' : take_form,'fields' : take_fields, 'state':[ ('end','Cancel'),('_create_case','Create Case')]}
        },
        '_create_case' : {
            'actions' : [],
            'result' : {'type' : 'action', 'action' : create_case}
        },
    }
wiz_new_case("labo.new.case")



class wiz_new_case_sample(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch' : take_form,'fields' : take_fields, 'state':[ ('end','Cancel'),('_create_case','Create Case')]}
        },
        '_create_case' : {
            'actions' : [],
            'result' : {'type' : 'action', 'action' : create_case_sample}
        },
    }
wiz_new_case_sample("sample.new.case")


