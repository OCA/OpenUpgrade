##############################################################################
#Copyright (c) 2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#                    Fabien Pinckaers <fp@tiny.Be>
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

from osv import fields
from osv import osv
import time
import ir
from mx import DateTime
import datetime
import pooler
from tools import config
import netsvc

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


class product_product(osv.osv):
    _inherit="product.product"
    _columns = {
        'isact':fields.boolean('Is Activity'),
                
    }
product_product()


class h_activity(osv.osv):
  
    _name='h.activity'
    _inherits={'product.product':'h_id'}
   
    _description='Housekeeping Activity'
    _columns = {
        'h_id': fields.many2one('product.product','Product_id'),
       }
    _defaults = {
        'isact': lambda *a: 1,
       }
#end class
h_activity()


class hotel_housekeeping(osv.osv):
    _name = "hotel.housekeeping"
    _description = "Reservation"
    _columns = {
        'current_date':fields.date("Today's Date",required=True),
        'clean_type':fields.selection([('daily','Daily'),('checkin','Checkin'),('checkout','Checkout')],'Clean Type',required=True),
        'room_no':fields.many2one('hotel.room','Room No',required=True),
        'activity_lines':fields.one2many('hotel.housekeeping.activities','a_list','Activities'),
        'room_no':fields.many2one('product.product','Room No',required=True),
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
        print "CANCEL"
        self.write(cr, uid, ids, {
            'state':'cancel'
        })
        
        return True

    def room_done(self, cr, uid, ids, *args):
        print "DONE"
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


  
#class housekeeping_activity(osv.osv):
#    _name = "housekeeping.activity"
#    _description = "Housekeeping Activity List"
#    _columns = {
#        'name':fields.char('Activity Name',size=64,required=True),
#        'categ_id':fields.many2one('product.category','Category', required=True, change_default=True),
#        }
##end class
#housekeeping_activity()

class hotel_housekeeping_activities(osv.osv):
    _name = "hotel.housekeeping.activities"
    _description = "Housekeeping Activities "
    _columns = {
        'a_list':fields.many2one('hotel.housekeeping'),
        'activity_name':fields.many2one('h.activity','Housekeeping Activity'),
        'housekeeper':fields.many2one('res.users','Housekeeper',required=True),
        'clean_start_time':fields.datetime('Clean Start Time',required=True),
        'clean_end_time':fields.datetime('Clean End Time',required=True),
        'dirty':fields.boolean('Dirty'),
        'clean':fields.boolean('Clean'),
 
        }
#end class
hotel_housekeeping_activities()


