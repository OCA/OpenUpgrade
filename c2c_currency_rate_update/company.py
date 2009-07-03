# -*- encoding: utf-8 -*-
#
#  company.py
#  l10n_ch
#
#  Created by Nicolas Bessi based on Credric Krier contribution
#
#  Copyright (c) 2009 CamptoCamp. All rights reserved.
##############################################################################
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

import netsvc
from osv import fields, osv
class res_company(osv.osv):
    """override company to add currency udate"""
    
    def _multi_curr_enable(self, cr, uid, ids, field_name, arg, context={}):
        "check if multiy company currency is enable"
        result = {}
        enable = 1
        try :
            #if we are in a mutli company mode the company_id col should exsits
            cr.execute('select company_id from res_currency')
            cr.fetchall()
        except:
            cr.rollback()
            enable = 0
        for id in ids:
            result[id] = enable
        return result
        
        
    def button_refresh_currency(self, cr, uid, ids, context=None):
        """Refrech  the currency !!for all the company
        now"""
        currency_updater_obj = self.pool.get('currency.rate.update')
        try:
            currency_updater_obj.run_currency_update(cr, uid)
        except Exception, e:
            print str(e)
            return False
        return True
        
        
    def _on_change_auto_currency_up(self, cr, uid, id, value):
        """handle the activation of the currecny update on compagnies.
        There are two ways of implementing mutli_company currency, 
        the currency is shared or not. The module take care of the two
        ways. If the currency are shared, you will only be able to set 
        auto update on one company, this will avoid to have unusefull cron 
        object running. 
        If yours currency are not share you will be able to activate the
        auto update on each separated company"""
        
        if len(id) :
            id = id[0]
        else :
            return {}
        enable = self.browse(cr, uid, id).multi_company_currency_enable
        compagnies =  self.search(cr, uid, [])
        activate_cron = 'f'
        if not value :
            # this statement is here beacaus we do no want to save in case of error
            self.write(cr, uid, id,{'auto_currency_up':value})
            for comp in compagnies :
                if self.browse(cr, uid, comp).auto_currency_up: 
                    activate_cron = 't'
                    break
            self.pool.get('currency.rate.update').save_cron(
                                                            cr, 
                                                            uid, 
                                                            {'active':activate_cron}
                                                        )
            return {}
        else :
            for comp in compagnies :
                if comp != id and not enable:
                    if self.browse(cr, uid, comp).multi_company_currency_enable:
                        #we ensure taht we did not have write a true value
                        self.write(cr, uid, id,{'auto_currency_up':False})
                        return {
                                'value':{ 
                                            'auto_currency_up':False
                                        },
                                        
                                'warning':{
                                            'title':"Warning",
                                            'message': 'Yon can not activate auto currency '+\
                                            'update on more thant one company with this '+
                                            'multi company configuration'
                                            }
                                }
            self.write(cr, uid, id,{'auto_currency_up':value})
            for comp in compagnies :
                if self.browse(cr, uid, comp).auto_currency_up: 
                    activate_cron = 't'
                self.pool.get('currency.rate.update').save_cron(
                                                            cr, 
                                                            uid, 
                                                            {'active':activate_cron}
                                                        )
                break
            return {}
                    
            
    def _on_change_intervall(self, cr, uid, id, interval) :
        ###Function that will update the cron
        ###freqeuence
        self.pool.get('currency.rate.update').save_cron(
                                                            cr, 
                                                            uid, 
                                                            {'interval_type':interval}
                                                        )
        compagnies =  self.search(cr, uid, [])
        for comp in compagnies :
            self.write(cr, uid, comp,{'interval_type':interval})
        return {}
        
    _inherit = "res.company"
    _columns = {
        ### activate the currency update
        'auto_currency_up': fields.boolean('Automatical update of the currency this company'),
        'services_to_use' : fields.one2many(
                                            'currency.rate.update.service', 
                                            'company_id',
                                            'Currency update services' 
                                            ),
        ###predifine cron frequence
        'interval_type': fields.selection(
                                                [
                                                    ('days','Day(s)'), 
                                                    ('weeks', 'Week(s)'), 
                                                    ('months', 'Month(s)')
                                                ],
                                                'Currency update frequence',
                                                help="""changing this value will
                                                 also affect other compagnies"""
                                            ),
        ###function field that allows to know the
        ###mutli company currency implementation                                    
        'multi_company_currency_enable' : fields.function(
                                            _multi_curr_enable, 
                                            method=True, 
                                            type='boolean', 
                                            string="Multi company currency",
                                            help='if this case is not check you can'+\
                                            ' not set currency is active on two company'
                                        ),
    }    
res_company()