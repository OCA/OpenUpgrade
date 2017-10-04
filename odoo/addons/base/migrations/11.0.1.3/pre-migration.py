# -*- coding: utf-8 -*-
# Copyright 2017 bloopark systems (<http://bloopark.de>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade
from odoo.addons.openupgrade_records.lib import apriori


# backup of
# - datetime field because it changes to date field
column_copies = {
    'res_currency_rate': [('name', None, None)],
}


# rename_tables is not needed because "ir.actions.report.xml" and
# "ir.actions.report" result both in "ir_act_report_xml"
model_renames_ir_actions_report = [
    ('ir.actions.report.xml', 'ir.actions.report')
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.update_module_names(
        env.cr, apriori.renamed_modules.items()
    )
    openupgrade.update_module_names(
        env.cr, apriori.merged_modules.items(), merge_modules=True)
    openupgrade.copy_columns(env.cr, column_copies)
    openupgrade.rename_models(env.cr, model_renames_ir_actions_report)
    env.cr.execute(
        """UPDATE ir_actions SET type = 'ir.actions.report'
        WHERE type = 'ir.actions.report.xml'""")

    rule_xml_ids = ('ir_config_parameter_rule', 'ir_values_default_rule')
    env.cr.execute(
        """ DELETE FROM ir_rule WHERE id IN (
                SELECT res_id FROM ir_model_data WHERE module = 'base'
                    AND name IN %s) """, (rule_xml_ids,))
    env.cr.execute(
        """ DELETE FROM ir_model_data WHERE module = 'base'
                AND name IN %s """, (rule_xml_ids,))

    # All existing server actions are of type server action
    env.cr.execute("UPDATE ir_act_server SET usage = 'ir_actions_server'")
    # work_days interval was removed from selection values
    env.cr.execute(
        """
        UPDATE ir_cron SET interval_type = 'days'
        WHERE interval_type = 'work_days'""")
