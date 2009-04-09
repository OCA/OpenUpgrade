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

from osv import osv, fields

class base_report_model(osv.osv):
    _name = 'base.report.model'
    _description = 'Visible models for a tool'
    _columns = {
    'name' : fields.char( 'Visible Name', size=64,required=True ),
    'model_id' : fields.many2one('ir.model', 'Model', delete='oncascade',required=True),
    }
    def model_change(self, cr,uid, ids, model_id, context={}):
        return {
            'value': {'name':self.pool.get('ir.model').browse(cr,uid,model_id).name}
        }
    _order = 'name'
base_report_model()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

