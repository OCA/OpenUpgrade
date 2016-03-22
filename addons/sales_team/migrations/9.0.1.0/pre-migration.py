# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenUpgrade module for Odoo
#    @copyright 2014-Today: Odoo Community Association
#    @author: Sylvain LE GAL <https://twitter.com/legalsylvain>
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

from openupgradelib import openupgrade


OBSOLETE_VIEWS = (
    'crm_case_section_salesteams_search',
    'crm_case_section_salesteams_view_kanban',
    'crm_case_section_view_form',
    'crm_case_section_view_tree',
    'res_user_form',
    'view_sale_config_settings',
    'view_users_form_preferences',
)


def recursive_delete(cr):
    """
    cannot delete because inherit_id
    cannot stitch when mode is extension
    """
    # openupgrade.logged_query(cr, """
    #     delete from ir_ui_view v
    #     using ir_model_data d where v.id=d.res_id
    #     and d.model = 'ir.ui.view' and d.module = 'sales_team'
    #     and d.name in {}
    #     """.format(OBSOLETE_VIEWS))
    cr.execute("""
        select res_id from ir_model_data d
        where d.model = 'ir.ui.view' and d.module = 'sales_team'
        and d.name in {}
        """.format(OBSOLETE_VIEWS))
    all_delete_ids = tuple()
    new_delete_ids = tuple(row[0] for row in cr.fetchall())
    while len(new_delete_ids) > 0:
        all_delete_ids += new_delete_ids
        cr.execute("""
            select id from ir_ui_view v
            where v.inherit_id in {}
            """.format(new_delete_ids))
        new_delete_ids = tuple(row[0] for row in cr.fetchall())
    openupgrade.logged_query(cr, """
        delete from ir_ui_view v
        where v.id in {}
        """.format(all_delete_ids))


@openupgrade.migrate()
def migrate(cr, version):
    # done here because res_partner.team_id must be valid
    openupgrade.rename_tables(cr, [('crm_case_section', 'crm_team'), ('crm_case_stage', 'crm_stage')])
    recursive_delete(cr)
