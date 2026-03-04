# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

_deleted_xmlids = [
    "account_payment.onboarding_onboarding_step_payment_provider",
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.delete_records_safely_by_xml_id(env, _deleted_xmlids)
