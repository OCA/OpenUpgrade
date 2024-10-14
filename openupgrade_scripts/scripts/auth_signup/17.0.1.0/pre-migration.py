# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_deleted_xml_records = ["auth_signup.reset_password_email"]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.delete_records_safely_by_xml_id(
        env,
        _deleted_xml_records,
    )
