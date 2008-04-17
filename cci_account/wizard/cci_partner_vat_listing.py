import wizard
import time
import datetime
import pooler
import tools

form = """<?xml version="1.0"?>
<form string="Select Fiscal Year">
    <label string="This wizard will create an XML file for Vat details and total invoiced amounts per human entity(Partner)."  colspan="4"/>
    <newline/>
    <field name="fyear" />
</form>"""

fields = {
    'fyear': {'string': 'Fiscal Year', 'type': 'many2one', 'relation': 'account.fiscalyear', 'required': True},
   }
msg_form = """<?xml version="1.0"?>
<form string="Notification">
     <separator string="XML File has been Created."  colspan="4"/>
     <field name="msg" colspan="4" nolabel="1"/>
</form>"""

msg_fields = {
  'msg': {'string':'File created', 'type':'text', 'size':'100','readonly':True},
}

class wizard_vat(wizard.interface):

    def _create_xml(self, cr, uid, data, context):

        datas=[]
        p_id_list=pooler.get_pool(cr.dbname).get('res.partner').search(cr,uid,[('vat','!=',False)])

        if not p_id_list:
             raise wizard.except_wizard('Data Insufficient!','No partner has a VAT Number asociated with him.')
        obj_year=pooler.get_pool(cr.dbname).get('account.fiscalyear').browse(cr,uid,data['form']['fyear'])
        period="to_date('" + str(obj_year.date_start) + "','yyyy-mm-dd') and to_date('" + str(obj_year.date_stop) +"','yyyy-mm-dd')"

        for p_id in p_id_list:
            record=[] # this holds record per partner
            obj_partner=pooler.get_pool(cr.dbname).get('res.partner').browse(cr,uid,p_id)

            record.append(obj_partner.vat)

            if not obj_partner.address:
                record.append('None')
            for ads in obj_partner.address:
                if ads.type=='default':
                    if ads.country_id:
                        record.append(ads.country_id.name)
                    else:
                        record.append('None')
            cr.execute('select a.type,sum(debit)-sum(credit) from account_move_line l left join account_account a on (l.account_id=a.id) where a.type in ('"'income'"','"'tax'"') and l.partner_id=%d and l.date between %s group by a.type'%(p_id,period))
            line_info=cr.fetchall()

            if len(line_info)==1:
                if line_info[0][0]=='income':
                       record.append(0.00)
                       record.append(line_info[0][1])
                else:
                       record.append(line_info[0][1])
                       record.append(0.00)
            else:
                for item in line_info:
                    record.append(item[1])
            datas.append(record)
        root_path=tools.config.options['root_path']
        file=open(root_path+'/partners_vat_listing.xml', 'w')
        file.write('<?xml version="1.0"?>\n<header>\n\tWelcome To TinyERP.Think Big, Use TinyERP.\n</header>\n')

        seq=0
        for line in datas:
            seq +=1
            file.write('<ClientList SequenceNum="'+str(seq)+'">\n\t<CompanyInfo>\n\t\t<VATNum>'+line[0] +'</VATNum>\n\t\t<Country>'+line[1] +'</Country>\n\t</CompanyInfo>\n\t<Amount>'+str(line[2]) +'</Amount>\n\t<TurnOver>'+str(line[3]) +'</TurnOver>\n</ClientList>\n')
        file.close()
        return {'msg':'partners_vat_listing.xml file has been created at '+root_path+'.' }

    states = {
        'init': {
            'actions': [],
            'result': {'type':'form', 'arch':form, 'fields':fields, 'state':[('end','Cancel'),('go','Create XML')]},
        },
        'go': {
            'actions': [_create_xml],
            'result': {'type':'form', 'arch':msg_form, 'fields':msg_fields, 'state':[('end','Ok')]},
        }

    }

wizard_vat('list.vat.detail')