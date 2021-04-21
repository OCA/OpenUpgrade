# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def fill_base_automation_ir_model_fields_rel(env):
    openupgrade.logged_query(
        env.cr,
        """
        WITH q1 AS (
            SELECT ba.id, unnest(
                string_to_array(ba.on_change_fields, ',')
            ) AS field, ias.model_id
            FROM base_automation ba
            JOIN ir_act_server ias ON ba.action_server_id = ias.id
            WHERE ba.on_change_fields is not null
        )
        INSERT INTO base_automation_onchange_fields_rel
            (base_automation_id, ir_model_fields_id)
        SELECT q1.id, imf.id
        FROM ir_model_fields AS imf
        JOIN q1 ON imf.name = q1.field
        WHERE imf.model_id = q1.model_id
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_base_automation_ir_model_fields_rel(env)
