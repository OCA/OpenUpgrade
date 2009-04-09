# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields
from osv import osv
import time
import ir
from mx import DateTime
import datetime
import pooler
from tools import config
import netsvc

class hotel_housekeeping(osv.osv):
    _name = "hotel.housekeeping"
    _description = "Reservation"
    _columns = {
        'current_date':fields.date("Today's Date",required=True),
        'clean_type':fields.selection([('daily','Daily'),('checkin','Checkin'),('checkout','Checkout')],'Clean Type',required=True),
        'room_no':fields.many2one('hotel.room','Room No',required=True),
        'activity_lines':fields.one2many('hotel.housekeeping.activities','a_list','Activities'),
        'room_no':fields.many2one('product.product','Room No',required=True),
        'activity_lines':fields.one2many('hotel.housekeeping.activities','a_list','Activities'),
        'inspector':fields.many2one('res.users','Inspector',required=True),
        'inspect_date_time':fields.datetime('Inspect Date Time',required=True),
        'quality':fields.selection([('good','Good'),('ok','Ok')],'Quality',required=True),
        'state': fields.selection([('dirty','Dirty'),('clean','Clean'),('inspect','Inspect'),('done','Done'),('cancel', 'Cancelled')], 'state', select=True, required=True, readonly=True),
       
        }
    _defaults={
        'state': lambda *a: 'dirty',
        'current_date':lambda *a: time.strftime('%Y-%m-%d'),
        }
    def action_set_to_dirty(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state': 'dirty'})
        wf_service = netsvc.LocalService('workflow')
        for id in ids:
            wf_service.trg_create(uid, self._name, id, cr)
        return True
    
    def room_cancel(self, cr, uid, ids, *args):

        self.write(cr, uid, ids, {
            'state':'cancel'
        })
        return True

    def room_done(self, cr, uid, ids, *args):

        self.write(cr, uid, ids, {
            'state':'done'
        })
        return True
    
    def room_inspect(self, cr, uid, ids, *args):

        self.write(cr, uid, ids, {
            'state':'inspect'
        })
        return True
    
    def room_clean(self, cr, uid, ids, *args):

        self.write(cr, uid, ids, {
            'state':'clean'
        })
        return True
    
    
    
    
#end class
hotel_housekeeping()  

class product_category(osv.osv):
    _inherit="product.category"
    _columns = {
        'isactivitytype':fields.boolean('Is Activity Type'),
    }
product_category()

class hotel_housekeeping_activity_type(osv.osv):
    _name='hotel.housekeeping.activity.type'
    _description='Activity Type'
    _inherits = {'product.category':'activity_id'}
    _columns = {
        'activity_id':fields.many2one('product.category','category',required=True),
       }
    _defaults = {
        'isactivitytype': lambda *a: 1,

    }
#end class
hotel_housekeeping_activity_type()
  
class housekeeping_activity(osv.osv):
    _name = "housekeeping.activity"
    _description = "Housekeeping Activity List"
    _columns = {
        'name':fields.char('Activity Name',size=64,required=True),
        'categ_id':fields.many2one('product.category','Category', required=True, change_default=True),
        }
#end class
housekeeping_activity()

class hotel_housekeeping_activities(osv.osv):
    _name = "hotel.housekeeping.activities"
    _description = "Housekeeping Activities "
    _columns = {
        'a_list':fields.many2one('hotel.housekeeping'),
        'activity_name':fields.many2one('housekeeping.activity','Housekeeping Activity'),
        'housekeeper':fields.many2one('res.users','Housekeeper'),
        'clean_start_time':fields.datetime('Clean Start Time',required=True),
        'clean_end_time':fields.datetime('Clean End Time',required=True),
        'dirty':fields.boolean('Dirty'),
        'clean':fields.boolean('Clean'),
 
        }
#end class
hotel_housekeeping_activities()

class product_category(osv.osv):
    _inherit="product.category"
    _columns = {
        'isactivitytype':fields.boolean('Is Activity Type'),
    }
product_category()

class hotel_housekeeping_activity_type(osv.osv):
    _name='hotel.housekeeping.activity.type'
    _description='Activity Type'
    _inherits = {'product.category':'activity_id'}
    _columns = {
        'activity_id':fields.many2one('product.category','category',required=True),
       }
    _defaults = {
        'isactivitytype': lambda *a: 1,

    }
#end class
hotel_housekeeping_activity_type()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

