# -*- coding: utf-8 -*-
# Copyright 2017 bloopark systems (<http://bloopark.de>)
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import csv
from psycopg2.extensions import AsIs
from odoo.addons.openupgrade_records.lib import apriori
from openupgradelib import openupgrade
from odoo.modules.module import get_module_resource


# backup of
# - datetime field because it changes to date field
column_copies = {
    'res_currency_rate': [('name', None, None)],
}
column_renames = {
    'ir_actions': [('usage', None)],
}


# rename_tables is not needed because "ir.actions.report.xml" and
# "ir.actions.report" result both in "ir_act_report_xml"
model_renames_ir_actions_report = [
    ('ir.actions.report.xml', 'ir.actions.report')
]


def fill_cron_action_server_pre(env):
    """Prefill the column with a fixed value for avoiding the not null error,
    but wait until post for filling correctly the field and related record.
    """
    openupgrade.add_fields(
        env, [
            ('ir_actions_server_id', 'ir.cron', 'ir_cron', 'many2one', False,
             'base'),
        ],
    )
    env.cr.execute("SELECT MIN(id) FROM ir_act_server")
    row = env.cr.fetchone()
    server_action_id = row and row[0] or 1
    # Write in the ir.cron record the parent ir.actions.server ID
    env.cr.execute(
        "UPDATE ir_cron SET ir_actions_server_id = %s",
        (server_action_id, ),
    )


def ensure_country_state_id_on_existing_records(cr):
    """Suppose you have country states introduced manually.
    This method ensure you don't have problems later in the migration when
    loading the res.country.state.csv"""
    with open(get_module_resource('base', 'res', 'res.country.state.csv'),
              newline='') as country_states_file:
        states = csv.reader(country_states_file, delimiter=',', quotechar='"')
        for row, state in enumerate(states):
            if row == 0:
                continue
            data_name = state[0]
            country_code = state[1]
            name = state[2]
            state_code = state[3]
            # first: query to ensure the existing odoo countries have
            # the code of the csv file, because maybe some code has changed
            cr.execute(
                """
                UPDATE res_country_state rcs
                SET code = '%(state_code)s'
                FROM ir_model_data imd
                WHERE imd.model = 'res.country.state'
                    AND imd.res_id = rcs.id
                    AND imd.name = '%(data_name)s'
                """ % {
                    'state_code': state_code,
                    'data_name': data_name,
                }
            )
            # second: find if csv record exists in ir_model_data
            cr.execute(
                """
                SELECT imd.id
                FROM ir_model_data imd
                INNER JOIN res_country_state rcs ON (
                    imd.model = 'res.country.state' AND imd.res_id = rcs.id)
                LEFT JOIN res_country rc ON rcs.country_id = rc.id
                INNER JOIN ir_model_data imd2 ON (
                    rc.id = imd2.res_id AND imd2.model = 'res.country')
                WHERE imd2.name = '%(country_code)s'
                    AND rcs.code = '%(state_code)s'
                    AND imd.name = '%(data_name)s'
                """ % {
                    'country_code': country_code,
                    'state_code': state_code,
                    'data_name': data_name,
                }
            )
            found_id = cr.fetchone()
            if found_id:
                continue
            # third: as csv record not exists in ir_model_data, search for one
            # introduced manually that has same codes
            cr.execute(
                """
                SELECT imd.id
                FROM ir_model_data imd
                INNER JOIN res_country_state rcs ON (
                    imd.model = 'res.country.state' AND imd.res_id = rcs.id)
                LEFT JOIN res_country rc ON rcs.country_id = rc.id
                INNER JOIN ir_model_data imd2 ON (
                    rc.id = imd2.res_id AND imd2.model = 'res.country')
                WHERE imd2.name = '%(country_code)s'
                    AND rcs.code = '%(state_code)s'
                ORDER BY imd.id DESC
                LIMIT 1
                """ % {
                    'country_code': country_code,
                    'state_code': state_code,
                }
            )
            found_id = cr.fetchone()
            if not found_id:
                continue
            # fourth: if found, ensure it has the same xmlid as the csv record
            openupgrade.logged_query(
                cr,
                """
                UPDATE ir_model_data
                SET name = '%(data_name)s', module = 'base'
                WHERE id = %(data_id)s AND model = 'res.country.state'
                """ % {
                    'data_name': data_name,
                    'data_id': found_id[0],
                }
            )
            cr.execute(
                """
                UPDATE res_country_state rcs
                SET name = $$%(name)s$$
                FROM ir_model_data imd
                WHERE imd.id = %(data_id)s
                    AND imd.model = 'res.country.state'
                    AND imd.res_id = rcs.id
                """ % {
                    'name': name,
                    'data_id': found_id[0],
                }
            )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.update_module_names(
        env.cr, apriori.renamed_modules.items()
    )
    openupgrade.update_module_names(
        env.cr, apriori.merged_modules.items(), merge_modules=True)
    openupgrade.copy_columns(env.cr, column_copies)
    openupgrade.rename_columns(env.cr, column_renames)
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
    env.cr.execute(
        """ ALTER TABLE ir_act_server ADD COLUMN usage VARCHAR;
        UPDATE ir_act_server SET usage = 'ir_actions_server'""")
    # For some window actions, there is a value in the old column
    # that was inherited from ir_actions before
    env.cr.execute(
        """ ALTER TABLE ir_act_window ADD COLUMN usage VARCHAR;
        UPDATE ir_act_window SET usage = %s""",
        (AsIs(openupgrade.get_legacy_name('usage')),))

    # work_days interval was removed from selection values
    env.cr.execute(
        """
        UPDATE ir_cron SET interval_type = 'days'
        WHERE interval_type = 'work_days'""")
    fill_cron_action_server_pre(env)
    ensure_country_state_id_on_existing_records(env.cr)
