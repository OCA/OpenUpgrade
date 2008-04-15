import wizard
import time
import datetime
import pooler
import tools

form = """<?xml version="1.0"?>
<form string="Notification">
     <separator string="XML Flie has been Created."  colspan="4"/>
     <field name="msg" colspan="4" nolabel="1"/>
</form>"""

fields = {
    'msg': {'string':'File created', 'type':'text', 'size':'100','readonly':True},
}

class wizard_vat_declaration(wizard.interface):

    def _create_xml(self, cr, uid, data, context):

        datas=[]
        cr.execute('select count(*) from account_tax_code')
        rows=cr.fetchone()

        if rows[0]==0:
            raise wizard.except_wizard('Data Insufficient!','No Records found in Tax Codes.')

        tax_ids=pooler.get_pool(cr.dbname).get('account.tax.code').search(cr,uid,[])
        tax_info=pooler.get_pool(cr.dbname).get('account.tax.code').read(cr,uid,tax_ids,['code','sum_period'])

        root_path=tools.config.options['root_path']
        file=open(root_path+'/vat_declaration.xml', 'w')
        file.write('<?xml version="1.0"?>\n<header>\n\tWelcome To TinyERP.Think Big, Use TinyERP.\n</header>\n<DATA>\n\t<DATA_ELEM>')

        for item in tax_info:
            if item['code']:
                if item['code'] == '71-72':
                    item['code']=71
                file.write('\n\t\t<D'+str(item['code']) +'>' + str(item['sum_period'])+  '</D'+str(item['code']) +'>')

        file.write('\n\t</DATA_ELEM>\n</DATA>')
        file.close()

        return {'msg':'vat_declaration.xml file has been created at '+root_path+'.' }

    states = {
        'init': {
            'actions': [_create_xml],
            'result': {'type':'form', 'arch':form, 'fields':fields, 'state':[('end','ok')]},
        }
    }

wizard_vat_declaration('cci.account.vat.declaration')