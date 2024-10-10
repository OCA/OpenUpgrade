# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_deleted_xml_records = [
    "base.icp_mail_bounce_alias",
    "base.icp_mail_catchall_alias",
    "base.icp_mail_default_from",
]


@openupgrade.migrate()
def migrate(env, version):
    """Call disable_invalid_filters in every edition of openupgrade"""
    openupgrade.disable_invalid_filters(env)
    openupgrade.delete_records_safely_by_xml_id(
        env,
        _deleted_xml_records,
    )
