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


# tuple is SQL-friendly
OBSOLETE_FILTERS = (
    'filter_crm_phonecall_delay_to_close',
    'filter_crm_phonecall_phone_call_to_do',
    'filter_crm_phonecall_sales_team',
    'filter_leads_country',
    'filter_leads_long_term_revenue',
    'filter_leads_overpassed_deadline',
    'filter_leads_revenue_per_lead',
    'filter_leads_salesperson',
    'filter_opportunity_top_opportunities',
)


OBSOLETE_VIEWS = (
    'crm_case_categ-view',
    'crm_case_categ_tree-view',
    'crm_case_inbound_phone_tree_view',
    'crm_case_phone_calendar_view',
    'crm_case_phone_form_view',
    'crm_case_phone_tree_view',
    'crm_case_section_salesteams_view_kanban',
    'crm_case_stage_form',
    'crm_case_stage_tree',
    'crm_segmentation-view',
    'crm_segmentation_line-view',
    'crm_segmentation_line_tree-view',
    'crm_segmentation_tree-view',
    'crm_tracking_campaign_form',
    'crm_tracking_campaign_tree',
    'crm_tracking_medium_view_form',
    'crm_tracking_medium_view_tree',
    'crm_tracking_source_view_form',
    'crm_tracking_source_view_tree',
    'phonecall_to_phonecall_view',
    'view_crm_case_phonecalls_filter',
    'view_crm_payment_mode_form',
    'view_crm_payment_mode_tree',
    'view_report_crm_lead_filter',
    'view_report_crm_lead_graph',
    'view_report_crm_lead_graph_two',
    'view_report_crm_opportunity_filter',
    'view_report_crm_opportunity_graph',
    'view_report_crm_phonecall_filter',
    'view_report_crm_phonecall_graph',
)


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.logged_query(cr, """
        delete from ir_ui_view v
        using ir_model_data d where v.id=d.res_id
        and d.model = 'ir.filters' and d.module = 'crm'
        and d.name in {}
        """.format(OBSOLETE_FILTERS))
    openupgrade.logged_query(cr, """
        delete from ir_ui_view v
        using ir_model_data d where v.id=d.res_id
        and d.model = 'ir.ui.view' and d.module = 'crm'
        and d.name in {}
        """.format(OBSOLETE_VIEWS))
