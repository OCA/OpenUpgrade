# Copyright 2018 Eficent <http://www.eficent.com>
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

column_copies = {
    'crm_team': [
        ('dashboard_graph_model', None, None),
    ],
}

_column_renames = {
    'crm_lead': [
        ('opt_out', None),
    ],
}

_field_renames = [
    # for preserving filters et al that have the same meaning
    ('crm.lead', 'crm_lead', 'opt_out', 'is_blacklisted'),
]

_xml_ids_renames = [
    ('crm.action_crm_tag_form_view_oppor11',
     'crm.crm_lead_opportunities_view_form'),
    ('crm.action_crm_tag_kanban_view_oppor11',
     'crm.crm_lead_opportunities_view_kanban'),
    ('crm.action_crm_tag_tree_view_oppor11',
     'crm.crm_lead_opportunities_view_tree'),
]


def identify_act_window_views(env):
    """Some action window views were previously declared directly from the
    one2many field of the parent, not having XML-IDs. In this new version,
    they are unfolded and given an XML-ID, provoking a constraint error as
    you can't have several views of the same type. We assign that XML-IDs here
    for solving the problems.
    """
    imd_obj = env['ir.model.data']
    mapping = [
        ('crm_lead_all_leads', 'crm_lead_all_leads_view_tree', 'tree'),
        ('crm_lead_all_leads', 'crm_lead_all_leads_view_kanban', 'kanban'),
        ('crm_lead_opportunities_tree_view',
         'crm_lead_opportunities_tree_view_view_calendar', 'calendar'),
        ('crm_lead_opportunities_tree_view',
         'crm_lead_opportunities_tree_view_view_form', 'form'),
        ('crm_lead_opportunities_tree_view',
         'crm_lead_opportunities_tree_view_view_graph', 'graph'),
        ('crm_lead_opportunities_tree_view',
         'crm_lead_opportunities_tree_view_view_kanban', 'kanban'),
        ('crm_lead_opportunities_tree_view',
         'crm_lead_opportunities_tree_view_view_pivot', 'pivot'),
        ('crm_lead_opportunities_tree_view',
         'crm_lead_opportunities_tree_view_view_tree', 'tree'),
    ]
    for act_xml_id, xml_id, view_mode in mapping:
        act_window = env.ref('crm.' + act_xml_id)
        imd_obj.create({
            'module': 'crm',
            'name': xml_id,
            'model': 'ir.actions.act_window.view',
            'res_id': act_window.view_ids.filtered(
                lambda x: x.view_mode == view_mode
            ).id,
        })


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(env.cr, column_copies)
    openupgrade.rename_columns(env.cr, _column_renames)
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.rename_xmlids(env.cr, _xml_ids_renames)
    identify_act_window_views(env)
