# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def switch_noupdate_records(env):
    openupgrade.set_xml_ids_noupdate_value(
        env,
        "maintenance",
        [
            "mail_act_maintenance_request",
            "mail_alias_equipment",
            "mt_cat_mat_assign",
            "mt_cat_req_created",
            "mt_mat_assign",
            "mt_req_created",
            "mt_req_status",
            "equipment_team_maintenance",
        ],
        True,
    )


@openupgrade.migrate()
def migrate(env, version):
    switch_noupdate_records(env)
