# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.set_xml_ids_noupdate_value(
        env,
        "digest",
        [
            "digest_tip_digest_0",
            "digest_tip_digest_1",
            "digest_tip_digest_2",
            "digest_tip_digest_3",
            "digest_tip_digest_4",
        ],
        False,
    )
