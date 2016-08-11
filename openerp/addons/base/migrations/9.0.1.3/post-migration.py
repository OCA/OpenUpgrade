# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenUpgrade module for Odoo
#    @copyright 2015-Today: Odoo Community Association
#    @author: Stephane LE CORNEC
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

import logging
from openupgradelib import openupgrade
from openerp.modules.registry import RegistryManager
from openerp import SUPERUSER_ID


logger = logging.getLogger('OpenUpgrade')


# copied from pre-migration
column_copies = {
    'ir_act_url': [
        ('help', None, None),
    ],
    'ir_act_window': [
        ('help', None, None),
    ],
    'ir_actions': [
        ('help', None, None),
    ],
    'ir_act_client': [
        ('help', None, None),
    ],
    'ir_act_report_xml': [
        ('help', None, None),
    ],
    'ir_act_server': [
        ('help', None, None),
    ],
}


# company_type must match is_company
def match_company_type_to_is_company(cr):
    openupgrade.logged_query(cr, """
        UPDATE res_partner
        SET company_type = (CASE WHEN is_company THEN 'company' ELSE 'person' END)
        """)


# updates to ir_ui_view will not clear inherit_id
def clear_inherit_id(cr):
    "report.layout used to inherit from web.layout, we must explicitely clear this now"
    openupgrade.logged_query(cr, """
        UPDATE ir_ui_view v
        SET inherit_id = null
        FROM ir_model_data d
        WHERE d.res_id = v.id
        AND d.module = 'report' AND d.name = 'layout'
        """)


def rename_your_company(cr):
    openupgrade.logged_query(cr, """
        UPDATE res_company r
        SET name = 'My Company'
        FROM ir_model_data d
        WHERE d.res_id = r.id
        AND d.module = 'base' AND d.name = 'main_company'
        AND r.name = 'Your Company'
        """)


def set_filter_active(cr):
    openupgrade.logged_query(cr, """
        UPDATE ir_filters
        SET active = True
        """)


def precalculate_checksum(cr):
    pool = RegistryManager.get(cr.dbname)
    ir_attachment = pool['ir.attachment']
    for attach_id in ir_attachment.search(cr, SUPERUSER_ID, []):
        attach = ir_attachment.browse(cr, SUPERUSER_ID, attach_id)
        # as done in ir_attachment._data_set()
        value = attach.db_datas
        bin_data = value and value.decode('base64') or ''  # empty string to compute its hash
        attach.checksum = attach._compute_checksum(bin_data)


def remove_obsolete_modules(cr, modules_to_remove):
    pool = RegistryManager.get(cr.dbname)
    ir_module_module = pool['ir.module.module']
    domain = [('name', 'in', modules_to_remove),
              ('state', 'in', ('installed', 'to install', 'to upgrade'))]
    ids = ir_module_module.search(cr, SUPERUSER_ID, domain)
    ir_module_module.module_uninstall(cr, SUPERUSER_ID, ids)


@openupgrade.migrate()
def migrate(cr, version):
    for table_name in column_copies.keys():
        for (old, new, field_type) in column_copies[table_name]:
            openupgrade.convert_field_to_html(cr, table_name, openupgrade.get_legacy_name(old), old)
    match_company_type_to_is_company(cr)
    clear_inherit_id(cr)
    rename_your_company(cr)
    set_filter_active(cr)
    precalculate_checksum(cr)
    remove_obsolete_modules(cr, ('web_gantt', 'web_graph', 'web_tests'))
    openupgrade.load_data(cr, 'base', 'migrations/9.0.1.3/noupdate_changes.xml')
