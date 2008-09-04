from osv import fields,osv
import tools
import urllib,urllib2
import time
from xml.dom import minidom
import pooler

class res_currency(osv.osv):
    _inherit = "res.currency"
   
    def get_currency_rate(self, cr, uid, ids=[], context={}):
        cur_obj = pooler.get_pool(cr.dbname).get('res.currency')
        cur_rate_obj = pooler.get_pool(cr.dbname).get('res.currency.rate')
        com_obj = pooler.get_pool(cr.dbname).get('res.company')
        
        companies = com_obj.search(cr, uid, [])
        for company in companies:
            code = com_obj.browse(cr, uid, company).currency_id.code
            
            cur_ids = cur_obj.search(cr, uid, [('company_id','=',company)])
            for cur in cur_obj.browse(cr, uid, cur_ids):
                if code==cur.code:
                    continue
                urldata = {'FromCurrency':code, 'ToCurrency':cur.code ,'method':'GET'}
                data = urllib.urlencode(urldata)
                req = urllib2.Request('http://www.webservicex.net/CurrencyConvertor.asmx/ConversionRate',data)
                
                try:
                    response = urllib2.urlopen(req)
                except Exception, e:
                    print 'Error : ', e
                
                data = response.read()
                xmldoc = minidom.parseString(data)
                rate = xmldoc.documentElement.firstChild.nodeValue
        
                if rate:
                    date = time.strftime('%Y-%m-%d')
                    cur_rate_obj.create(cr, uid, {'name': date , 'rate':rate, 'currency_id': cur.id})
        return True
    
res_currency()
