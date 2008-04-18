import wizard
import time
import datetime
import pooler
import base64

form = """<?xml version="1.0"?>
<form string="Notification">
     <separator string="XML Flie has been Created."  colspan="4"/>
     <field name="msg" colspan="4" nolabel="1"/>
     <field name="file_save" />
</form>"""

fields = {
    'msg': {'string':'File created', 'type':'text', 'size':'100','readonly':True},
    'file_save':{'string': 'Save File',
        'type': 'binary',
        'readonly': True,},
}

class wizard_vat_declaration(wizard.interface):

    def _create_xml(self, cr, uid, data, context):

        list_of_tags=['00','01','02','03','45','46','47','48','49','54','55','56','57','59','61','62','63','64','71','81','82','83','84','85','86','87','91']

        tax_ids=pooler.get_pool(cr.dbname).get('account.tax.code').search(cr,uid,[])
        tax_info=pooler.get_pool(cr.dbname).get('account.tax.code').read(cr,uid,tax_ids,['code','sum_period'])

        data_of_file='<?xml version="1.0"?>\n<header>\n\tWelcome To TinyERP.Think Big, Use TinyERP.\n</header>\n<DATA>\n\t<DATA_ELEM>'

        for item in tax_info:
            if item['code']:
                if item['code'] == '71-72':
                    item['code']='71'
                if item['code'] in list_of_tags:
                    data_of_file +='\n\t\t<D'+str(int(item['code'])) +'>' + str(int(item['sum_period']*100)) +  '</D'+str(int(item['code'])) +'>'

        data_of_file +='\n\t</DATA_ELEM>\n</DATA>'
        data['form']['msg']='Save the File with '".xml"' extension.'
        data['form']['file_save']=base64.encodestring(data_of_file)
        return data['form']


    states = {
        'init': {
            'actions': [_create_xml],
            'result': {'type':'form', 'arch':form, 'fields':fields, 'state':[('end','ok')]},
        }
    }

wizard_vat_declaration('cci.account.vat.declaration')