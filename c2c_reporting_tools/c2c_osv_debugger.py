# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) Camptocamp SA
# Author: Arnaud Wüst
#
#
#    This file is part of the c2c_report_tools module.
#
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
from osv import fields, osv



class c2c_osv_debugger(osv.osv):
    """ this class is used to debbug a class. inherit (in python way, not openerp way) your class from this one instead of osv.osv to get traces of methods call """
    
    # define the level of output to print
    # print_level = 0 --> print nothing
    # print_level = 10 --> print only which method is called
    # print_level = 20 --> print also the params and return values of the call
    PRINT_LEVEL = 20

    def name_search(self, cr, user, obj, name, args,context={}):
        if self.PRINT_LEVEL >= 10: 
            print 'c2cdebug NAME_SEARCH call. '
        
        if self.PRINT_LEVEL >= 20:
            print '  user:    ', user
            print '  obj:     ', obj
            print '  name:    ', name
            print '  args:    ',args
            print '  context: ', context

        result = super(c2c_osv_debugger,self).name_search(cr,user,obj,name,args,context)

        if self.PRINT_LEVEL >= 20:
            print 'c2cdebug NAME_SEARCH result: ', result
        return result
    
    
    def search(self, cr, user, args, offset=0, limit=None, order=None, context=None, count=False):
        if self.PRINT_LEVEL >= 10:
            print 'c2cdebug: SEARCH called'

        if self.PRINT_LEVEL >= 20:    
            print '  user:    ', user
            print '  args:    ', args
            print '  offset:  ', offset
            print '  limit:   ', limit
            print '  order:   ', order
            print '  context: ', context
            print '  count:   ', count
        
        result = super(c2c_osv_debugger,self).search(cr,user,args,offset=offset,limit=limit,order=order,context=context,count=count)
        
        if self.PRINT_LEVEL >= 20:
            print 'c2cdebug: SEARCH result: ', result
        return result
    
      
    def create(self, cr, user, vals, context=None):
        if self.PRINT_LEVEL >= 10:
            print 'c2cdebug: CREATE called'
        if self.PRINT_LEVEL >= 20:
            print '   user:   ', user
            print '   vals:   ', vals
            print '  context: ', context
        
        result = super(c2c_osv_debugger,self).create(cr, user, vals, context=context)

        if self.PRINT_LEVEL >= 20:
            print 'c2cdebug: CREATE result: ', result
        return result
    
    
    def read(self, cr, user, ids, fields=None, context=None, load='_classic_read'):       
        if self.PRINT_LEVEL >= 10:
            print 'c2cdebug: READ called'
        if self.PRINT_LEVEL >= 20:
            print '  user:    ', user
            print '  ids:     ', ids
            print '  fields:  ', fields
            print '  context: ', context
            print '  load:    ', load        
        
        result = super(c2c_osv_debugger,self).read(cr, user, ids, fields=fields, context=context, load=load)

        if self.PRINT_LEVEL >= 20:
            print 'c2cdebug: READ result: ', result
        return result
    
        
    def write(self, cr, user, ids, vals, context=None):        
        if self.PRINT_LEVEL >= 10:
            print 'c2cdebug: WRITE called'
        if self.PRINT_LEVEL >= 20:
            print '  user:    ', user
            print '  ids:     ', ids
            print '  vals:    ', vals
            print '  context: ', context

        result = super(c2c_osv_debugger,self).write(cr, user, ids, vals, context=context)

        if self.PRINT_LEVEL >= 20:
            print 'c2cdebug: WRITE result: ', result
        return result
    
    def browse(self, cr, uid, select, context=None, list_class=None):
        if self.PRINT_LEVEL >= 10:
            print 'c2cdebug: BROWSE called'
        if self.PRINT_LEVEL >= 20:
            print '  uid:        ', uid
            print '  select:     ', select
            print '  context:    ', context
            print '  list_class: ', list_class
        
        result = super(c2c_osv_debugger,self).browse(cr, uid, select, context=context, list_class=list_class)

        if self.PRINT_LEVEL >= 20:
            print 'c2cdebug: BROWSE result: ', result
        return result
    
    def default_get(self, cr, uid, fields, context=None):
        if self.PRINT_LEVEL >= 10:
            print 'c2cdebug: DEFAULT_GET called'
        if self.PRINT_LEVEL >= 20:
            print '  uid:     ', uid
            print '  fields:  ', fields
            print '  context: ', context

        result = super(c2c_osv_debugger,self).default_get(cr, uid, fields, context=context);

        if self.PRINT_LEVEL >= 20:
            print 'c2cdebug: DEFAULT_GET result: ', result
        return result
    
    def copy(self, cr, uid, id, default=None, context=None):
        if self.PRINT_LEVEL >= 10:
            print 'c2cdebug: COPY called'
        if self.PRINT_LEVEL >= 20:
            print '  uid:     ', uid
            print '  id:      ', id
            print '  default: ', default
            print '  context: ', context

        result = super(c2c_osv_debugger,self).copy(cr, uid, id, default=default, context=context)

        if self.PRINT_LEVEL >= 20:
            print 'c2cdebug: COPY result: ', result
        return result
    
    
    def unlink(self, cr, uid, ids, context=None):
        if self.PRINT_LEVEL >= 10:
            print 'c2cdebug: UNLINK called'
        if self.PRINT_LEVEL >= 20:
            print '  uid:     ', uid
            print '  ids:      ', ids
            print '  context: ', context

        result = super(c2c_osv_debugger, self).unlink(cr, uid, ids, context=context)
        if self.PRINT_LEVEL >= 20:
            print 'c2cdebug: UNLINK result: ', result
        return result

        
    def name_get(self, cr, user, ids, context=None):
        if self.PRINT_LEVEL >= 10:
            print 'c2cdebug: NAME_GET called'
        if self.PRINT_LEVEL >= 20:
            print '  user:    ', user
            print '  ids:     ', ids
            print '  context: ', context
        
        
        result = super(c2c_osv_debugger,self).name_get(cr, user, ids, context=context)
        if self.PRINT_LEVEL >= 20:
            print 'c2cdebug: NAME_GET result: ', result
        return result
    
    def search_count(self, cr, user, args, context=None):
        if self.PRINT_LEVEL >= 10:
            print 'c2cdebug: SEARCH_COUNT called'
        if self.PRINT_LEVEL >= 20:
            print '  user:    ', user
            print '  args:    ', args
            print '  context: ', context

        result = super(c2c_osv_debugger,self).search_count(cr, user, args, context=context)

        if self.PRINT_LEVEL >= 20:
            print 'c2cdebug: SEARCH_COUNT result: ', result
        return result
    
    def fields_get(self, cr, user, fields=None, context=None):
        if self.PRINT_LEVEL >= 10:
            print 'c2cdebug: FIELDS_GET called'
        if self.PRINT_LEVEL >= 20:
            print '  user:    ', user
            print '  fields:  ', fields
            print '  context: ', context
    
        result = super(c2c_osv_debugger,self).fields_get(cr, user, fields=fields, context=context)

        if self.PRINT_LEVEL >= 20:
            print 'c2cdebug: FIELDS_GET result: ', result
        return result
        
    def fields_view_get(self, cr, user, view_id=None, view_type='form', context=None, toolbar=False):
        if self.PRINT_LEVEL >= 10:
            print 'c2cdebug: FIELDS_VIEW_GET called'
        if self.PRINT_LEVEL >= 20:
            print '  user:      ', user
            print '  view_id:   ', view_id
            print '  view_type: ', view_type
            print '  context:   ', context
            print '  toolbar:   ', toolbar

        result = super(c2c_osv_debugger,self).fields_view_get(cr, user, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar)

        if self.PRINT_LEVEL >= 20:
            print 'c2cdebug: FIELDS_VIEW_GET result: ', result
        return result
        
    def view_header_get(self, cr, user, view_id=None, view_type='form', context=None):
        if self.PRINT_LEVEL >= 10:
            print 'c2cdebug: VIEW_HEADER_GET called'
        if self.PRINT_LEVEL >= 20:
            print '  user:      ', user
            print '  view_id:   ', view_id
            print '  view_type: ', view_type
            print '  context:   ', context

        result = super(c2c_osv_debugger,self).view_header_get(cr, user, view_id=view_id, view_type=view_type, context=context)

        if self.PRINT_LEVEL >= 20:
            print 'c2cdebug: VIEW_HEADER_GET result: ', result
        return result
        
    def distinct_field_get(self, cr, uid, field, value, args=None, offset=0, limit=None):
        if self.PRINT_LEVEL >= 10:
            print 'c2cdebug: DISTINCT_FIELD_GET called'
        if self.PRINT_LEVEL >= 20:
            print '  uid:       ', user
            print '  field:     ', view_id
            print '  value:     ', view_type
            print '  args:      ', args
            print '  offset:    ', offset
            print '  limit:     ', limit

        result = super(c2c_osv_debugger,self).distinct_field_get(cr, uid, field, value, args=args, offset=offset, limit=limit)

        if self.PRINT_LEVEL >= 20:
            print 'c2cdebug: DISTINCT_FIELD_GET result: ', result
        return result