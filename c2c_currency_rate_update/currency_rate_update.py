# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008 Camptocamp SA
# @author Nicolas Bessi 
# @source JBA and AWST inpiration 
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

from osv import osv, fields
import time
from mx import DateTime
from datetime import datetime, timedelta
import netsvc
import string

class Currency_rate_update_service(osv.osv):
    """Class thats tell for wich services wich currencies 
    have to be updated"""
    _name = "currency.rate.update.service"
    _description = "Currency Rate Update"
    _columns = {
                    ##list of webservicies the value sould be a class name 
                    'service' : fields.selection( 
                                                    [
                                                    ('Admin_ch_getter','Admin.ch'),
                                                    #('ECB_getter','European Central Bank'),
                                                    #('NYFB_getter','Federal Reserve Bank of NY'),                                                    
                                                    #('Google_getter','Google Finance'),
                                                    ('Yahoo_getter','Yahoo Finance '),
                                                    ],
                                                    "Webservice to use",
                                                    required = True
                                                ),
                     ##list of currency to update                           
                    'currency_to_update' : fields.many2many(
                                                            'res.currency',
                                                            'res_curreny_auto_udate_rel',
                                                            'service_id',
                                                            'currency_id',
                                                            'currency to update with this service',
                                                            ),
                    #back ref 
                    'company_id' : fields.many2one(
                                                    'res.company',
                                                    'linked company',
                                                    ),
                    ##note fileds that will be used as a logger
                    'note':fields.text('update notice')
                }
    _sql_constraints = [
                            (
                                'curr_service_unique', 
                                'unique (service, company_id)', 
                                _('You can use a service one time per company !')
                            )
                        ]

Currency_rate_update_service()

class Currency_rate_update(osv.osv):
    """Class that handle an ir cron call who will 
    update currencies based on a web url"""
    _name = "currency.rate.update"
    _description = "Currency Rate Update"
    ##dict that represent a cron object
    cron = {
            'active'          : False,
            'priority'        : 1,
            'interval_number' : 1,
            'interval_type'   : 'weeks',
            'nextcall'        : time.strftime("%Y-%m-%d %H:%M:%S", (datetime.today() + timedelta(days=1)).timetuple() ), #tomorrow same time
            'numbercall'      : -1,
            'doall'           : True,
            'model'           : 'currency.rate.update',
            'function'        : 'run_currency_update',
            'args'            : '()',    
    }
        
    logger = netsvc.Logger()
    LOG_NAME = 'cron-rates'
    MOD_NAME = 'c2c_currency_rate_update: '
    def get_cron_id(self, cr, uid, context):
        """return the updater cron's id. Create one if the cron does not exists """
        
        cron_id = 0
        cron_obj = self.pool.get('ir.cron')
        try: 
            #find the cron that send messages
            cron_id = cron_obj.search(
                                        cr, 
                                        uid,  
                                        [
                                            ('function', 'ilike', self.cron['function']), 
                                            ('model', 'ilike', self.cron['model'])
                                        ], 
                                        context={
                                                    'active_test': False
                                                } 
                                    )
            cron_id = int(cron_id[0])
        except Exception,e :
            self.logger.notifyChannel(
                                        self.LOG_NAME, 
                                        netsvc.LOG_INFO, 
                                        'warning cron not found one will be created'
                                     )
            print 'warning cron not found one will be created'
            pass # ignore if the cron is missing cause we are going to create it in db
        
        #the cron does not exists
        if not cron_id :
            #translate
            self.cron['name'] = _('Currency Rate Update')
            cron_id = cron_obj.create(cr, uid, self.cron, context)
        
        return cron_id
        
    def save_cron(self, cr, uid, datas, context={}):
        """save the cron config data should be a dict"""
        #modify the cron
        cron_id = self.get_cron_id(cr, uid, context)        
        result = self.pool.get('ir.cron').write(cr, uid, [cron_id], datas)    

    def run_currency_update(self, cr, uid):
        "update currency at the given frequence"
        factory = Currency_getter_factory()
        curr_obj = self.pool.get('res_currency')
        rate_obj = self.pool.get('res.currency.rate')
        companies = self.pool.get('res.company').search(cr, uid, [])
        for comp in self.pool.get('res.company').browse(cr, uid, companies):
            ##the multi company currency can beset or no so we handle 
            ##the two case
            if not comp.auto_currency_up :
                continue
            #we initialise the multi compnay search filter or not serach filter
            search_filter = []
            if comp.multi_company_currency_enable :
                search_filter = [('company_id','=',comp.id)]
            #we fetch the main currency. The main rate should be set at  1.00
            main_curr = comp.currency_id.code
            for service in comp.services_to_use :
                note = service.note and service.note or ''
                try :
                    ## we initalize the class taht will handle the request
                    ## and return a dict of rate
                    getter = factory.register(service.service)
                    curr_to_fetch = map(lambda x : x.code, service.currency_to_update)
                    res = getter.get_updated_currency(curr_to_fetch, main_curr)
                    rate_name = time.strftime('%Y-%m-%d')
                    for curr in service.currency_to_update :
                        if curr.code == main_curr :
                            continue
                        do_create = True
                        for rate in curr.rate_ids :
                            if rate.name == rate_name :
                                rate.write({'rate':res[curr.code]})
                                do_create = False
                                break
                        if do_create :
                            vals = {
                                        'currency_id': curr.id,
                                        'rate':res[curr.code],
                                        'name': rate_name
                                    }
                            rate_obj.create(    
                                            cr,
                                            uid,
                                            vals,
                                        )
                     
                    note = note + "\n currency updated at %s "\
                        %(str(datetime.today()))
                    service.write({'note':note})
                except Exception, e:
                    error_msg = note + "\n !!! %s %s !!!"\
                        %(str(datetime.today()), str(e))
                    self.logger.notifyChannel(self.LOG_NAME, netsvc.LOG_INFO, str(e))
                    service.write({'note':error_msg})
                
                
Currency_rate_update()

### Error Definition as specified in python 2.6 PEP
class AbstractClassError(Exception): 
    def __str__(self):
        return 'Abstarct Class'
    def __repr__(self):
     return 'Abstarct Class'

class AbstractMethodError(Exception):
    def __str__(self):
        return 'Abstarct Method'
    def __repr__(self):
        return 'Abstarct Method'

class UnknowClassError(Exception): 
    def __str__(self):
        return 'Unknown Class'
    def __repr__(self):
        return 'Unknown Class'
class UnsuportedCurrencyError(Exception): 
    def __init__(self, value):
           self.curr = value
    def __str__(self):
        return 'Unsupported currency '+self.curr
    def __repr__(self):
        return 'Unsupported currency '+self.curr
        
### end of error definition        
class Currency_getter_factory():
    """Factory pattern class that will return 
    a currency getter class base on the name passed
    to the register method"""
    def register(self, class_name): 
        allowed = [
                          'Admin_ch_getter',
                          'ECB_getter',
                          'NYFB_getter',
                          'Google_getter',
                          'Yahoo_getter',
                    ]
        if class_name in allowed:
            class_def = eval(class_name)
            return class_def()
        else :
            raise UnknowClassError
        

class Curreny_getter_interface(object) :
    "Abstract class of currency getter"
    
    supported_currency_array = \
['AFN', 'ALL', 'DZD', 'USD', 'USD', 'USD', 'EUR', 'AOA', 'XCD', 'XCD', 'ARS',
'AMD', 'AWG', 'AUD', 'EUR', 'AZN', 'EUR', 'BSD', 'BHD', 'EUR', 'BDT', 'BBD', 
'XCD', 'BYR', 'EUR', 'BZD', 'XOF', 'BMD', 'BTN', 'INR', 'BOB', 'ANG', 'BAM', 
'BWP', 'NOK', 'BRL', 'GBP', 'USD', 'USD', 'BND', 'BGN', 'XOF', 'MMK', 'BIF', 
'XOF', 'USD', 'KHR', 'XAF', 'CAD', 'EUR', 'CVE', 'KYD', 'XAF', 'XAF', 'CLP', 
'CNY', 'AUD', 'AUD', 'COP', 'XAF', 'KMF', 'XPF', 'XAF', 'CDF', 'NZD', 'CRC', 
'HRK', 'CUP', 'ANG', 'EUR', 'CYP', 'CZK', 'DKK', 'DJF', 'XCD', 'DOP', 'EUR', 
'XCD', 'IDR', 'USD', 'EGP', 'EUR', 'SVC', 'USD', 'GBP', 'XAF', 'ETB', 'ERN', 
'EEK', 'ETB', 'EUR', 'FKP', 'DKK', 'FJD', 'EUR', 'EUR', 'EUR', 'XPF', 'XPF', 
'EUR', 'XPF', 'XAF', 'GMD', 'GEL', 'EUR', 'GHS', 'GIP', 'XAU', 'GBP', 'EUR', 
'DKK', 'XCD', 'XCD', 'EUR', 'USD', 'GTQ', 'GGP', 'GNF', 'XOF', 'GYD', 'HTG', 
'USD', 'AUD', 'BAM', 'EUR', 'EUR', 'HNL', 'HKD', 'HUF', 'ISK', 'INR', 'IDR', 
'XDR', 'IRR', 'IQD', 'EUR', 'IMP', 'ILS', 'EUR', 'JMD', 'NOK', 'JPY', 'JEP', 
'JOD', 'KZT', 'AUD', 'KES', 'AUD', 'KPW', 'KRW', 'KWD', 'KGS', 'LAK', 'LVL', 
'LBP', 'LSL', 'ZAR', 'LRD', 'LYD', 'CHF', 'LTL', 'EUR', 'MOP', 'MKD', 'MGA', 
'EUR', 'MWK', 'MYR', 'MVR', 'XOF', 'EUR', 'MTL', 'FKP', 'USD', 'USD', 'EUR', 
'MRO', 'MUR', 'EUR', 'AUD', 'MXN', 'USD', 'USD', 'EUR', 'MDL', 'EUR', 'MNT', 
'EUR', 'XCD', 'MAD', 'MZN', 'MMK', 'NAD', 'ZAR', 'AUD', 'NPR', 'ANG', 'EUR', 
'XCD', 'XPF', 'NZD', 'NIO', 'XOF', 'NGN', 'NZD', 'AUD', 'USD', 'NOK', 'OMR', 
'PKR', 'USD', 'XPD', 'PAB', 'USD', 'PGK', 'PYG', 'PEN', 'PHP', 'NZD', 'XPT', 
'PLN', 'EUR', 'STD', 'USD', 'QAR', 'EUR', 'RON', 'RUB', 'RWF', 'STD', 'ANG', 
'MAD', 'XCD', 'SHP', 'XCD', 'XCD', 'EUR', 'XCD', 'EUR', 'USD', 'WST', 'EUR', 
'SAR', 'SPL', 'XOF', 'RSD', 'SCR', 'SLL', 'XAG', 'SGD', 'ANG', 'ANG', 'EUR', 
'EUR', 'SBD', 'SOS', 'ZAR', 'GBP', 'GBP', 'EUR', 'XDR', 'LKR', 'SDG', 'SRD', 
'NOK', 'SZL', 'SEK', 'CHF', 'SYP', 'TWD', 'RUB', 'TJS', 'TZS', 'THB', 'IDR', 
'TTD', 'XOF', 'NZD', 'TOP', 'TTD', 'TND', 'TRY', 'TMM', 'USD', 'TVD', 'UGX', 
'UAH', 'AED', 'GBP', 'USD', 'USD', 'UYU', 'USD', 'UZS', 'VUV', 'EUR', 'VEB', 
'VEF', 'VND', 'USD', 'USD', 'USD', 'XPF', 'MAD', 'YER', 'ZMK', 'ZWD']

    ##updated currency this arry will contain the final result
    updated_currency = {}
    
    def __init__(self) :
        """Constructor tha ensure taht the Abstract class is
        not instanciated"""
        raise AbstractClassError
    
    def get_updated_currency(self, currency_array, main_currency) :
        """Interface method that will retriev the currency
           This function has to be reinplemented in child"""
        raise AbstractMethodError
    
    def validate_cur(self, currency) :
        """Validate if the currency to update is supported"""
        if currency not in self.supported_currency_array :
            raise UnsuportedCurrencyError(currency)        
        
    def get_url(self, url):
        """Retrun a string of a get url query"""
        try:
            import urllib
            objfile = urllib.urlopen(url)
            rawfile = objfile.read()
            objfile.close()
            return rawfile
        except ImportError:
            raise osv.except_osv('Error !', self.MOD_NAME+'Unable to import urllib !')
        except IOError:
            raise osv.except_osv('Error !', self.MOD_NAME+'Web Service does not exist !')
            
#Yahoo ###################################################################################     
class Yahoo_getter(Curreny_getter_interface) :
    """Implementation of Currency_getter_factory interface
    for Yahoo finance service"""
    def __init__(self):
        pass
    def get_updated_currency(self, currency_array, main_currency):
        """implementation of abstract method of Curreny_getter_interface"""
        self.validate_cur(main_currency)
        url='http://download.finance.yahoo.com/d/quotes.txt?s="%s"=X&f=sl1c1abg'
        if main_currency in currency_array :
            currency_array.remove(main_currency)
        for curr in currency_array :
            self.validate_cur(curr)
            res = self.get_url(url%(main_currency+curr))
            val = res.split(',')[1]
            if val :
                self.updated_currency[curr] = val
            else :
                raise Exception('Could not update the %s'%(curr))
        return self.updated_currency
##Admin CH ############################################################################    
class Admin_ch_getter(Curreny_getter_interface) :
    """Implementation of Currency_getter_factory interface
    for Admin.ch service"""
    def __init__(self):
        pass
        
    def rate_retrieve(self, node) :
        """ Parse a dom node to retviev 
        currencies data"""
        res = {}
        if isinstance(node, list) :
            node = node[0]
        res['code'] = node.attributes['code'].value.upper()
        res['currency'] = node.getElementsByTagName('waehrung')[0].childNodes[0].data
        res['rate_currency'] = float(node.getElementsByTagName('kurs')[0].childNodes[0].data)
        res['rate_ref'] = float(res['currency'].split(' ')[0])
        return res

    def get_updated_currency(self, currency_array, main_currency):
        """implementation of abstract method of Curreny_getter_interface"""
        url='http://www.afd.admin.ch/publicdb/newdb/mwst_kurse/wechselkurse.php'
        #we do not want to update the main currency
        if main_currency in currency_array :
            currency_array.remove(main_currency)
        from xml.dom.minidom import parseString
        from xml import xpath
        rawfile = self.get_url(url)        
        dom = parseString(rawfile)
        #we dynamically update supported currencies
        self.supported_currency_array = []
        self.supported_currency_array.append('CHF')
        for el in xpath.Evaluate("/wechselkurse/devise/@code", dom):
            self.supported_currency_array.append(el.value.upper())
        self.validate_cur(main_currency)
        #The XML give the value in franc for 1 XX if we are in CHF 
        #we want to have the value for 1 xx in chf
        #if main currency is not CHF we have to apply a computation on it
        if main_currency != 'CHF':
            main_xpath = "/wechselkurse/devise[@code='%s']"%(main_currency.lower())
            node = xpath.Evaluate(main_xpath, dom)
            tmp_data = self.rate_retrieve(node)
            main_rate = tmp_data['rate_currency'] / tmp_data['rate_ref']
        for curr in currency_array :
            curr_xpath = "/wechselkurse/devise[@code='%s']"%(curr.lower())
            for node  in xpath.Evaluate(curr_xpath, dom):    
                tmp_data = self.rate_retrieve(node)
                #Source is in CHF, so we transform it into reference currencies
                if main_currency == 'CHF' :
                    rate = 1 / (tmp_data['rate_currency'] / tmp_data['rate_ref'])
                else :
                    rate = main_rate / (tmp_data['rate_currency'] / tmp_data['rate_ref'])

                self.updated_currency[curr] = rate
        return self.updated_currency