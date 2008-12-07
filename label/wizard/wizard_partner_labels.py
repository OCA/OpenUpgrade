# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008 Zikzakmedia. (http://zikzakmedia.com) All Rights Reserved.
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

import wizard
import pooler

form='''<?xml version="1.0" encoding="utf-8"?>
<form string="Label Report Options">
    <field name="label_format" colspan="4"/>
    <separator string="Printer Margins" colspan="4"/>
    <field name="printer_top"/>
    <field name="printer_bottom"/>
    <field name="printer_left"/>
    <field name="printer_right"/>
    <separator string="Label Char Font" colspan="4"/>
    <field name="font_type"/>
    <field name="font_size"/>
    <separator string="First Label" colspan="4"/>
    <field name="first_row"/>
    <field name="first_col"/>
</form>'''

fields={
    'label_format': {'string':'Label Format', 'type':'many2one', 'relation':'report.label', 'required':'true'},
    'printer_top':    {'string':'Top',    'type':'char', 'size':20, 'help':"Numeric size ended with the unit (cm or in). For example, 0.3cm or 0.2in"},
    'printer_bottom': {'string':'Bottom', 'type':'char', 'size':20, 'help':"Numeric size ended with the unit (cm or in). For example, 0.3cm or 0.2in"},
    'printer_left':   {'string':'Left',   'type':'char', 'size':20, 'help':"Numeric size ended with the unit (cm or in). For example, 0.3cm or 0.2in"},
    'printer_right':  {'string':'Right',  'type':'char', 'size':20, 'help':"Numeric size ended with the unit (cm or in). For example, 0.3cm or 0.2in"},
    'font_type': {'string':"Font Type", 'type':'selection', 'required':'true', 'selection':[('Times-Roman','Times-Roman'),('Times-Bold','Times-Bold'),('Times-Italic','Times-Italic'),('Times-BoldItalic','Times-BoldItalic'),('Helvetica','Helvetica'),('Helvetica-Bold','Helvetica-Bold'),('Helvetica-Oblique','Helvetica-Oblique'),('Helvetica-BoldOblique','Helvetica-BoldOblique'),('Courier','Courier'),('Courier-Bold','Courier-Bold'),('Courier-Oblique','Courier-Oblique'),('Courier-BoldOblique','Courier-BoldOblique')]},
    'font_size': {'string':"Font Size", 'type':'selection', 'required':'true', 'selection':[('6','6'),('7','7'),('8','8'),('9','9'),('10','10'),('11','11'),('12','12'),('14','14'),]},
    'first_row': {'string': 'First Row', 'type': 'integer', 'help': 'The Row of the first label in the first page'},
    'first_col': {'string': 'First Column', 'type': 'integer', 'help': 'The Column of the first label in the first page'},
}

top_form='''<?xml version="1.0" encoding="utf-8"?>
<form string="Notification">
<label string="Printer top margin bigger than (top label margin + label height). Try again." colspan="4"/>
</form>'''

bottom_form='''<?xml version="1.0" encoding="utf-8"?>
<form string="Notification">
<label string="Printer bottom margin bigger than (bottom label margin + label height). Try again." colspan="4"/>
</form>'''

left_form='''<?xml version="1.0" encoding="utf-8"?>
<form string="Notification">
<label string="Printer left margin bigger than (left label margin + label width). Try again." colspan="4"/>
</form>'''

right_form='''<?xml version="1.0" encoding="utf-8"?>
<form string="Notification">
<label string="Printer right margin bigger than (right label margin + label width). Try again." colspan="4"/>
</form>'''



def size2cm(text):
    """Converts the size text ended with 'cm' or 'in' to the numeric value in cm and returns it"""
    if text:
        if text[-2:] == "cm":
            return float(text[:-2])
        elif text[-2:] == "in":
            return float(text[:-2]) * 2.54
    return 0


class wizard_report(wizard.interface):
    def _init(self, cr, uid, data, context):
        data['form']['first_row'] = 1
        data['form']['first_col'] = 1
        return data['form']

    def _compute(self, cr, uid, data, context):
        data['form']['printer_top']    = size2cm(data['form']['printer_top'])
        data['form']['printer_bottom'] = size2cm(data['form']['printer_bottom'])
        data['form']['printer_left']   = size2cm(data['form']['printer_left'])
        data['form']['printer_right']  = size2cm(data['form']['printer_right'])
        pool = pooler.get_pool(cr.dbname)
        label = pool.get('report.label').browse(cr, uid, data['form']['label_format'])
        data['form']['page_width'] = size2cm(label.landscape and label.pagesize_id.height or label.pagesize_id.width)
        data['form']['page_height'] = size2cm(label.landscape and label.pagesize_id.width or label.pagesize_id.height)
        data['form']['rows'] = label.rows
        data['form']['cols'] = label.cols
        data['form']['label_width'] = size2cm(label.label_width)
        data['form']['label_height'] = size2cm(label.label_height)
        data['form']['width_incr'] = size2cm(label.width_incr)
        data['form']['height_incr'] = size2cm(label.height_incr)
        data['form']['initial_left_pos'] = size2cm(label.margin_left)

        # initial_bottom_pos = label.pagesize_id.height - label.margin_top - label.label_height
        mtop = size2cm(label.margin_top)
        data['form']['initial_bottom_pos'] = data['form']['page_height'] - mtop - data['form']['label_height']

        if data['form']['printer_top'] > mtop + data['form']['label_height']:
            return 'notify_top'
        if data['form']['printer_left'] > data['form']['initial_left_pos'] + data['form']['label_width']:
            return 'notify_left'
        if data['form']['printer_bottom'] > data['form']['page_height'] - mtop - (data['form']['rows']-1) * data['form']['height_incr']:
            return 'notify_bottom'
        if data['form']['printer_right'] >  data['form']['page_width'] - data['form']['initial_left_pos'] - (data['form']['cols']-1) * data['form']['width_incr']:
            return 'notify_right'
        return 'report'

    def _print(self, cr, uid, data, context):
        return data['form']

    states={
        'init':{
            'actions':[_init],
            'result':{'type':'form', 'arch':form, 'fields':fields, 'state':[('end', 'Cancel'), ('check', 'Print')]}
        },
        'check': {
            'actions': [],
            'result': {'type':'choice','next_state':_compute}
        },
        'notify_top': {
            'actions': [],
            'result': {'type':'form','arch':top_form,'fields':{},'state':[('end','Ok')]}
        },
        'notify_bottom': {
            'actions': [],
            'result': {'type':'form','arch':bottom_form,'fields':{},'state':[('end','Ok')]}
        },
        'notify_left': {
            'actions': [],
            'result': {'type':'form','arch':left_form,'fields':{},'state':[('end','Ok')]}
        },
        'notify_right': {
            'actions': [],
            'result': {'type':'form','arch':right_form,'fields':{},'state':[('end','Ok')]}
        },
        'report':{
            'actions':[_print],
            'result':{'type':'print', 'report':'res.partner.address.label', 'state':'end'}
        }
    }
wizard_report('res.partner.address.label')

