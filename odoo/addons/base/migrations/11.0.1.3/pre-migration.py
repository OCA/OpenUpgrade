# -*- coding: utf-8 -*-
# Copyright 2017 bloopark systems (<http://bloopark.de>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade
from odoo.addons.openupgrade_records.lib import apriori


# backup of deleted columns
column_renames = {
    'ir_act_url': [
        ('usage', None),
    ],
    'ir_actions': [
        ('usage', None),
    ],
    'ir_act_client': [
        ('usage', None),
    ],
    'ir_act_report_xml': [
        ('ir_values_id', None),
        ('header', None),
        ('parser', None),
        ('auto', None),
        ('report_xsl', None),
        ('report_xml', None),
        ('report_rml', None),
        ('report_sxw_content_data', None),
        ('report_rml_content_data', None),
    ],
    'ir_act_server': [
        ('action_id', None),
        ('condition', None),
        ('copyvalue', None),
        ('id_object', None),
        ('id_value', None),
        ('link_new_record', None),
        ('menu_ir_values_id', None),
        ('model_object_field', None),
        ('ref_object', None),
        ('sub_model_object_field', None),
        ('sub_object', None),
        ('use_create', None),
        ('use_relational_model', None),
        ('use_write', None),
        ('wkf_field_id', None),
        ('wkf_model_id', None),
        ('wkf_transition_id', None),
        ('write_expression', None),
    ],
    'ir_actions_todo': [
        ('note', None),
        ('type', None),
    ],
    'ir_cron': [
        ('args', None),
        ('function', None),
        ('model', None),
    ],
    'res_bank': [
        ('fax', None),
    ],
    'res_company': [
        ('custom_footer', None),
        ('font', None),
        ('rml_footer', None),
        ('rml_header', None),
        ('rml_header1', None),
        ('rml_header2', None),
        ('rml_header3', None),
        ('rml_paper_format', None),
    ],
    'res_partner': [
        ('fax', None),
    ],
}


# backup of
# - selection fields because their options changed
# - datetime field because it changes to date field
column_copies = {
    'ir_act_report_xml': [
        ('report_type', None, None),
    ],
    'ir_act_server': [
        ('usage', None, None),
    ],
    'ir_cron': [
        ('interval_type', None, None),
    ],
    'res_currency_rate': [
        ('name', None, None),
    ],
}


# rename_tables is not needed because "ir.actions.report.xml" and
# "ir.actions.report" result both in "ir_act_report_xml"
model_renames_ir_actions_report = [
    ('ir.actions.report.xml', 'ir.actions.report')
]


xmlid_renames = [
    ('report.paperformat_euro', 'base.paperformat_euro'),
    ('report.paperformat_us', 'base.paperformat_us'),
]


def update_module_names(cr):
    """Update module names from report to base completely and from portal to
    base partially."""
    openupgrade.update_module_names(
        cr,
        [
            ('report', 'base'),
        ],
        merge_modules=True
    )

    new_name = 'base'
    old_name = 'portal'
    if not openupgrade.is_module_installed(cr, old_name):
        return

    # get moved model fields
    moved_fields = tuple(['is_portal'])
    cr.execute("""
        SELECT id
        FROM ir_model_fields
        WHERE model IN ('res.groups') AND name in %s
    """, (moved_fields,))
    field_ids = tuple([r[0] for r in cr.fetchall()])

    # update ir_model_data, the subselect allows to avoid duplicated XML-IDs
    query = ("UPDATE ir_model_data SET module = %s "
             "WHERE module = %s AND res_id IN %s AND name NOT IN "
             "(SELECT name FROM ir_model_data WHERE module = %s)")
    openupgrade.logged_query(cr, query, (new_name, old_name, field_ids,
                                         new_name))

    # update ir_translation
    query = ("UPDATE ir_translation SET module = %s "
             "WHERE module = %s AND res_id IN %s")
    openupgrade.logged_query(cr, query, (new_name, old_name, field_ids))


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    openupgrade.update_module_names(
        cr, apriori.renamed_modules.iteritems()
    )

    openupgrade.rename_columns(env.cr, column_renames)
    openupgrade.copy_columns(env.cr, column_copies)
    openupgrade.rename_models(env.cr, model_renames_ir_actions_report)
    openupgrade.rename_xmlids(env.cr, xmlid_renames)
    update_module_names(env.cr)

    # Remove security rules
    env.ref('base.ir_config_parameter_rule').unlink()
    env.ref('base.ir_values_default_rule').unlink()
