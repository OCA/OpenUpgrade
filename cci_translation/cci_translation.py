##############################################################################
#
# Copyright (c) 2004 TINY SPRL. (http://tiny.be) All Rights Reserved.
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

import netsvc
import time
from osv import fields, osv

class translation_dossier(osv.osv):
    _name = 'translation.dossier'
    _desctiption = 'Translation Dossier'
    _columns = {
        'awex_eligible':fields.boolean('AWEX Eligible'),
        'awex_amount':fields.float('AWEX Amount')
                }
translation_dossier()

class credit_line(osv.osv):
    _name = 'credit.line'
    _desctiption = 'Credit line'
    _columns = {
        'from_date':fields.date('From Date'),
        'to_date':fields.date('To Date'),
        'global_credit':fields.float('Global Credit'),
        'customer_credit':fields.float('Customer Credit')
                }
credit_line()

class letter_credence(osv.osv):
    _name = 'letter.credence'
    _desctiption = 'Letter of Credence'
    _columns = {
        'emission_date':fields.date('Emission Date'),
        'asked_amount':fields.float('Asked Amount')
                }
letter_credence()

class res_partner(osv.osv):
    _inherit = 'res.partner'
    _desctiption = 'Partner'
    _columns = {
        'awex_eligible':fields.selection([('unknown','Unknown'),('yes','Yes'),('no','No')], "AWEX Eligible"),
                }
res_partner()

class translation_billing_line(osv.osv):
    _inherit = 'cci_missions.embassy_folder_line'
    _desctiption = 'Translation Billing Line'
    _columns = {
        'awex_eligible':fields.boolean('AWEX Eligible'),
        'awex_amount':fields.float('AWEX Amount')
                }
translation_billing_line()