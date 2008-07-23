# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004-2008 Tiny SPRL (http://tiny.be) All Rights Reserved.
#
# $Id$
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
###############################################################################

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

