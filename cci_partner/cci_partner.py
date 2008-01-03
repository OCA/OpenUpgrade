##############################################################################
#
# Copyright (c) 2007 TINY SPRL. (http://tiny.be) All Rights Reserved.
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

class res_partner(osv.osv):
    _inherit = "res.partner"
    _description = "res.partner"
    _columns = {
        'employee_nbr': fields.integer('Nbr of Employee (Area)',help="Nbr of Employee in the area of the CCI"),
        'employee_nbr_total':fields.integer('Nbr of Employee (Tot)',help="Nbr of Employee all around the world"),
        'invoice_paper':fields.selection([('virement','virement'),('belge','belge'),('virement','virement'),('iban','iban')], 'Bank Transfer Type',required=True),
        'invoice_public':fields.boolean('Invoice Public'),
        'invoice_special':fields.boolean('Invoice Special'),
        'state_id':fields.char('Partner State',size=20,help='status of activity of the partner'),#should be corect
        'state_id2':fields.char('Customer State',size=20,help='status of the partner as a customer'),#should be corect
        'activity_description':fields.text('Activity Description',traslate=True),
        'export_procent':fields.char('Export(%)',size=20),#should be corect
        'export_year':fields.date('Export date',help='year of the export_procent value'),#should be corect
        'import_procent':fields.char('Import (%)',size=20),#should be corect
        'import_year':fields.date('Import Date',help='year of the import_procent value'),#should be corect
        'domiciliation':fields.char('Domiciliation',size=20),#should be corect
        'domiciliation_cotisation':fields.char('Domiciliation (cotisation)',size=20,help='year of the import_procent value'),#should be corect
        'invoice_nbr':fields.char('Nbr of invoice to print',size=20,help='number of additive invoices to be printed for this customer'),#should be corect
        'name_official':fields.char('Official Name',size=80),
        'name_old':fields.char('Former Name',size=80),
        'wall_exclusion':fields.boolean('In Walloon DB',help='exclusion of this partner from the walloon database'),
        'mag_send':fields.selection([('Never','Never'),('Always','Always'),('Managed_by_Poste','Managed_by_Poste'),('Prospect','Prospect')], 'Send mag.',required=True),
        'date_founded':fields.date('Founding Date',help='Date of foundation of this company'),
        'training_authorization':fields.char('Training Auth.',size=12,help='Formation Checks Authorization number'),
        'lang_authorization':fields.char('Lang. Auth.',size=12,help='Language Checks Authorization number'),
        'alert_advertising':fields.boolean('Adv.Alert',help='Partners description to be shown when inserting new advertising sale'),
        'alert_events':fields.boolean('Event Alert',help='Partners description to be shown when inserting new subscription to a meeting'),
        'alert_legalisations':fields.boolean('Legal. Alert',help='Partners description to be shown when inserting new legalisation'),
        'alert_membership':fields.boolean('Membership Alert',help='Partners description to be shown when inserting new membership sale'),
        'alert_others':fields.boolean('Other alert',help='Partners description to be shown when inserting new sale not treated by _advertising, _events, _legalisations, _Membership'),
        'dir_name':fields.char('Name in Menber Dir.',size=250,help='Name under wich the partner will be inserted in the members directory'),
        'dir_name2':fields.char('1st Shortcut name ',size=250,help='First shortcut in the members directory, pointing to the dir_name field'),
        'dir_name3':fields.char('2nd Shortcut name ',size=250,help='Second shortcut'),
        'dir_date_last':fields.date('Partner Data Date',help='Date of latest update of the partner data by itself (via paper or Internet)'),
        'dir_date_accept':fields.date('“Bon à tirer” Date',help='Date of last acceptation of Bon à Tirer'),
        'dir_presence':fields.boolean('Dir. Presence',help='Présence dans le répertoire des entreprises'),
        'dir_date_publication:':fields.date('Publication Date'),
        'dir_exclude':fields.boolean('Dir. exclude',help='Exclusion from the Members directory'),
        #Never,Always,Managed_by_Poste,Prospect
        #virement belge,virement iban
        }
    _defaults = {
                 'wall_exclusion' : lambda *a: False,
                 'dir_presence' : lambda *a: False,
                 'dir_exclude':lambda *a: False,
                 }
res_partner()
