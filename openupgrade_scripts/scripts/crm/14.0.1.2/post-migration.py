# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "crm", "14.0.1.2/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(
        env, ["crm.crm_pls_rebuild_threshold_param"]
    )
