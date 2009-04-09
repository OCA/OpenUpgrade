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
from osv import osv

class report_intrastat_code(osv.osv):
    _inherit = "report.intrastat.code"

    def name_get(self, cr, user, ids, context={}):
        if not len(ids):
            return []
        def formating(r):
            if r['description'] and r['name']:
                return(r['id'], r['description']+' - '+r['name'])
            return(r['id'], (r['description'] or '')+(r['name'] or ''))
        
        return [formating(r) for r in self.read(cr, user, ids, ['name','description'], context)]

    _sql_constraints = [
                ('both_not_null', 'CHECK (name is not null or description is not null)', \
                 'Please provide at least a code or a description')]

report_intrastat_code()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

