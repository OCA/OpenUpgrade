# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 HacBee (<http://hbee.eu>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import pooler
from openerp.openupgrade import openupgrade
from openerp import SUPERUSER_ID

ACCOUNT_TYPE_XMLID_MAP = [
    ('l10n_be.user_type_capitaux', 'account.data_account_type_liability'),
    ('l10n_be.user_type_immo', 'account.data_account_type_asset'),
    ('l10n_be.user_type_tiers_receiv', 'account.data_account_type_receivable'),
    ('l10n_be.user_type_tiers_payable', 'account.data_account_type_payable'),
    ('l10n_be.user_type_tax', 'account.data_account_type_receivable'),
    ('l10n_be.user_type_financiers', 'account.data_account_type_cash'),
    ('l10n_be.user_type_charge', 'account.data_account_type_expense'),
    ('l10n_be.user_type_produit', 'account.data_account_type_income'),
]

def _get_id(cr, xml_id):
    pool = pooler.get_pool(cr.dbname)
    ir_model_data_obj = pool.get('ir.model.data')
    module, xml_id = xml_id.split('.')
    model, res_id = ir_model_data_obj.get_object_reference(cr, SUPERUSER_ID,
                        module, xml_id)
    return res_id

def map_account_types(cr):
    for oldxmlid, newxmlid in ACCOUNT_TYPE_XMLID_MAP:
        old_id = _get_id(cr, oldxmlid)
        new_id = _get_id(cr, newxmlid)
        cr.execute("""
            UPDATE account_account
            SET user_type = %s
            WHERE user_type = %s
        """, (new_id, old_id))

@openupgrade.migrate()
def migrate(cr, version):
    map_account_types(cr)
