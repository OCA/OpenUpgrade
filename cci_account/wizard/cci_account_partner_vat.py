import wizard
import time
import datetime
import pooler
import xml.dom.ext
import xml.dom.minidom

form = """<?xml version="1.0"?>
<form string="Select Fiscal Year">
    <label string="This wizard will create an XML file for Vat details and total invoiced amounts per human entity(Partner)."  colspan="4"/>
    <newline/>
    <field name="fyear" />
</form>"""

fields = {
    'fyear': {'string': 'Fiscal Year', 'type': 'many2one', 'relation': 'account.fiscalyear', 'required': True},
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
            cr.execute('select id from account_invoice where partner_id=%d and date_invoice between %s and state='"'paid'"''%(p_id,period))
            invoice_ids=cr.fetchall()
            inv_list=[x[0] for x in invoice_ids]

            if not inv_list:
                continue
            sum_vat=0.00
            sum_tot=0.00
            for invoice in inv_list:
                obj_invoice=pooler.get_pool(cr.dbname).get('account.invoice').browse(cr,uid,invoice)
                sum_vat +=obj_invoice.amount_tax
                sum_tot +=obj_invoice.amount_total
            record.append(sum_vat)
            record.append(sum_tot)
            datas.append(record)
        file=open('vat_amount_detail.xml', 'w')
        file.write('<?xml version="1.0"?>\n<header>\n\tWelcome To TinyERP.Thing Big, Use TinyERP.\n</header>\n')

        seq=0
        for line in datas:
            seq +=1
            file.write('<ClientList SequenceNum="'+str(seq)+'">\n\t<CompanyInfo>\n\t\t<VATNum>"'+line[0] +'"</VATNum>\n\t\t<Country>"'+line[1] +'"</Country>\n\t</CompanyInfo>\n\t<Amount>"'+str(line[2]) +'"</Amount>\n\t<TurnOver>"'+str(line[3]) +'"</TurnOver>\n</ClientList>\n')
        file.close()
        return data['form']

    states = {
        'init': {
            'actions': [],
            'result': {'type':'form', 'arch':form, 'fields':fields, 'state':[('end','Cancel'),('go','Create XML')]},
        },
        'go': {
            'actions': [],
            'result': {'type':'action', 'action':_create_xml, 'state':'end'},
        },
    }

wizard_vat('list.vat.detail')