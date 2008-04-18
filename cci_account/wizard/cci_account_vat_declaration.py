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

        obj_company=pooler.get_pool(cr.dbname).get('res.company').browse(cr,uid,1)
        vat_no=obj_company.partner_id.vat
        if not vat_no:
            raise wizard.except_wizard('Data Insufficient','No VAT Number Associated with Main Company!')

        tax_ids=pooler.get_pool(cr.dbname).get('account.tax.code').search(cr,uid,[])
        tax_info=pooler.get_pool(cr.dbname).get('account.tax.code').read(cr,uid,tax_ids,['code','sum_period'])

        address=post_code=city=''
        if not obj_company.partner_id.address:
                address=post_code=city=''

        for ads in obj_company.partner_id.address:
                if ads.type=='default':
                    if ads.city:
                        city=ads.city
                    if ads.zip_id:
                        post_code=ads.zip.id.name
                    if ads.street:
                        address=ads.street
                    if ads.street2:
                        address +=ads.street2

        year_id=pooler.get_pool(cr.dbname).get('account.fiscalyear').find(cr, uid)
        current_year=pooler.get_pool(cr.dbname).get('account.fiscalyear').browse(cr,uid,year_id).name

        data_of_file='<?xml version="1.0"?>\n<VATSENDING xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="MultiDeclarationTVA-NoSignature-14.xml">'
        data_of_file +='\n\t<DECLARER>\n\t\t<VATNUMBER>'+str(vat_no)+'</VATNUMBER>\n\t\t<NAME>'+str(obj_company.name)+'</NAME>\n\t\t<ADDRESS>'+str(address)+'</ADDRESS>'
        data_of_file +='\n\t\t<POSTCODE>'+str(post_code)+'</POSTCODE>\n\t\t<CITY>'+str(city)+'</CITY>\n\t\t<SENDINGREFERENCE></SENDINGREFERENCE>\n\t</DECLARER>'
        data_of_file +='\n\t<VATRECORD>\n\t\t<RECNUM>1</RECNUM>\n\t\t<VATNUMBER>'+str(vat_no)+'</VATNUMBER>\n\t\t<DPERIODE>\n\t\t\t<MONTH>12</MONTH>\n\t\t\t<YEAR>'+str(current_year[-4:])+'</YEAR>\n\t\t</DPERIODE>\n\t\t<ASK RESTITUTION="NO" PAYMENT="NO"/>'
        data_of_file +='\n\t\t<DATA>\n\t\t\t<DATA_ELEM>'

        for item in tax_info:
            if item['code']:
                if item['code'] == '71-72':
                    item['code']='71'
                if item['code'] in list_of_tags:
                    data_of_file +='\n\t\t\t\t<D'+str(int(item['code'])) +'>' + str(int(item['sum_period']*100)) +  '</D'+str(int(item['code'])) +'>'

        data_of_file +='\n\t\t\t</DATA_ELEM>\n\t\t</DATA>\n\t</VATRECORD>\n</VATSENDING>'
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