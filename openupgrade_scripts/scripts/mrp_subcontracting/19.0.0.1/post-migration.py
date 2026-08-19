# Copyright 2026 Heliconia Solutions Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env,
        "mrp_subcontracting",
        "19.0.0.1/noupdate_changes.xml",
        xml_transformation_filename="19.0.0.1/noupdate_changes-transformation.xml",
    )
