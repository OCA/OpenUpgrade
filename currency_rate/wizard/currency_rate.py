import wizard
import pooler
import time
import urllib,urllib2
from xml.dom import minidom

_currency_form = '''<?xml version="1.0"?>
<form string="Currency Rate">
    <field name="from_cur" />
    <field name="to_cur"/>
    <field name="amount"/>
</form>'''

_currency_fields = {
    'from_cur': {'string': 'Currency From', 'type': 'many2one','relation':'res.currency','required':True},
    'to_cur': {'string': 'Currency To', 'type': 'many2one','relation':'res.currency','required':True},
    'amount': {'string': 'Amount', 'type': 'float'},
}

_result_form = '''<?xml version="1.0"?>
<form string="Result">   
    <field name="final_amount"/>
    <field name="rate"/>
</form>'''

_result_fields = {   
    'final_amount': {'string': 'Amount', 'type': 'float'},
    'rate': {'string': 'Current Rate', 'type': 'float'},
}


class wizard_currency_rate(wizard.interface):
    
    def _convert(self, cr, uid, data, context):
        res={}
        try:
            cur_obj = pooler.get_pool(cr.dbname).get('res.currency')
            
            from_cur_id = data['form']['from_cur']
            to_cur_id = data['form']['to_cur']
            amount = data['form']['amount']
           
            from_code = cur_obj.browse(self.cr, self.uid, from_cur_id).code
            to_code = cur_obj.browse(self.cr, self.uid, to_cur_id).code
            
            urldata = {'FromCurrency':from_code, 'ToCurrency':to_code ,'method':'GET'}
            data = urllib.urlencode(urldata)
            req = urllib2.Request('http://www.webservicex.net/CurrencyConvertor.asmx/ConversionRate',data)
            response = urllib2.urlopen(req)
            
            data = response.read()
            xmldoc = minidom.parseString(data)
            rate = xmldoc.documentElement.firstChild.nodeValue
        
            if rate:
                res['final_amount'] = (amount * rate) or 0.0
                res['rate'] = rate
        except:
            return res
        return res
        
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':_currency_form, 'fields':_currency_fields, 'state':[('end','Cancel'),('convert','Convert')]}
        },
         'convert': {
            'actions': [_convert],
            'result': {'type': 'form', 'arch':_result_form, 'fields':_result_fields, 'state':[('init','Back'),('end','Exit')]}
        }
    }
wizard_currency_rate('currency.rate')