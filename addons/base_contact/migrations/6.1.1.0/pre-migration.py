# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2012 Therp BV (<http://therp.nl>).
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

from openerp.openupgrade import openupgrade

def _migrate_last_name(cr):
    column_renames = {
        'res_partner_contact': [
            ('name', 'last_name'),
            ],
        }
    openupgrade.rename_columns(cr, column_renames)

def _migrate_birthdate(cr):
    openupgrade.logged_query(cr, 'alter table res_partner_contact alter column birthdate type character varying(64);')

@openupgrade.migrate()
def migrate(cr, version):
    _migrate_last_name(cr)
    _migrate_birthdate(cr)
