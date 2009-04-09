# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                    Jordi Esteve <jesteve@zikzakmedia.com>
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

from osv import osv, fields


class report_pagesize(osv.osv):
    _name = 'report.pagesize'
    _columns = {
        'name': fields.char('Name', size=20, required=True),
        'width': fields.char('Width', size=20, required=True, help="Numeric width of the page ended with the unit (cm or in). For example, A4 is 21cm and letter is 8.5in"),
        'height': fields.char('Height', size=20, required=True, help="Numeric height of the page ended with the unit (cm or in). For example, A4 is 29.7cm and letter is 11in"),
    }
    _order = 'name'

    def _check_unit(self, cr, uid, ids):
        for page in self.browse(cr, uid, ids):
            if page.width[-2:] not in ['cm', 'in']:
                return False
            if page.height[-2:] not in ['cm', 'in']:
                return False
        return True

    _constraints = [
        (_check_unit, 'Error! The page sizes do not have the unit (cm or in) at the end.', [])
    ]

report_pagesize()


class report_label_manufacturer(osv.osv):
    _name = 'report.label.manufacturer'
    _columns = {
        'name': fields.char('Name', size=50, required=True),
    }
    _order = 'name'

report_label_manufacturer()


class report_label(osv.osv):
    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        res = []
        for r in self.browse(cr, uid, ids):
            name = str(r.manufacturer_id.name or '') + ". " + str(r.name)
            res.append((r.id, name))
        return res

    _name = 'report.label'
    _columns = {
        'name': fields.char('Name', size=200, required=True),
        'manufacturer_id': fields.many2one('report.label.manufacturer', 'Manufacturer'),
        'description': fields.text('Description'),
        'pagesize_id': fields.many2one('report.pagesize', 'Page Size', required=True),
        'landscape': fields.boolean('Landscape', help="No check -> Portrait. Check -> Landscape"),
        'rows': fields.integer('Number of Rows', size=2, required=True),
        'cols': fields.integer('Number of Columns', size=2, required=True),
        'label_width': fields.char('Label Width', size=20, required=True, help="Numeric value ended with the unit (cm or in). For example 29.7cm or 11in"),
        'label_height': fields.char('Label Height', size=20, required=True, help="Numeric value ended with the unit (cm or in). For example 29.7cm or 11in"),
        'width_incr': fields.char('Width Increment', size=20, required=True, help="Width between start positions of 2 labels. Numeric value ended with the unit (cm or in). For example 29.7cm or 11in"),
        'height_incr': fields.char('Height Increment', size=20, required=True, help="Height between start positions of 2 labels. Numeric value ended with the unit (cm or in). For example 29.7cm or 11in"),
        'margin_top': fields.char('Top Margin', size=20, required=True, help="Numeric value ended with the unit (cm or in). For example 29.7cm or 11in"),
        'margin_left': fields.char('Left Margin', size=20, required=True, help="Numeric value ended with the unit (cm or in). For example 29.7cm or 11in"),
        #'margin_bottom': fields.char('Bottom Margin', size=20, required=True, help="Numeric value ended with the unit (cm or in). For example 29.7cm or 11in"),
        #'margin_right': fields.char('Right Margin', size=20, required=True, help="Numeric value ended with the unit (cm or in). For example 29.7cm or 11in"),
    }
    _defaults = {
    }
    _order = 'name'

    def _check_unit(self, cr, uid, ids):
        for label in self.browse(cr, uid, ids):
            if label.label_width[-2:] not in ['cm', 'in']:
                return False
            if label.label_height[-2:] not in ['cm', 'in']:
                return False
            if label.width_incr[-2:] not in ['cm', 'in']:
                return False
            if label.height_incr[-2:] not in ['cm', 'in']:
                return False
            if label.margin_top[-2:] not in ['cm', 'in']:
                return False
            if label.margin_left[-2:] not in ['cm', 'in']:
                return False
        return True

    _constraints = [
        (_check_unit, 'Error! Some sizes do not have the unit (cm or in) at the end.', [])
    ]

report_label()


