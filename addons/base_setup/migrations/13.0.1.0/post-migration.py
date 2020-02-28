# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

unlink_by_xmlid = [
    'base_setup.web_dashboard_menu',
    'base_setup.dashboard_qunit_suite',
]


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    openupgrade.delete_records_safely_by_xml_id(env, unlink_by_xmlid)
