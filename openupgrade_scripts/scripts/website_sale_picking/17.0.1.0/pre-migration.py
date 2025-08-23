# Copyright 2025 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_noupdate_xmlids = ["payment_provider_onsite"]
_xmlid_renames = [
    (
        "website_sale_picking.checkout_payment",
        "website_sale_picking.payment_method_form",
    )
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.set_xml_ids_noupdate_value(
        env, "website_sale_picking", _noupdate_xmlids, False
    )
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
