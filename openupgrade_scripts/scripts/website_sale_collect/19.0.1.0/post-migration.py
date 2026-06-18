# Copyright 2026 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def _mark_pickup_auxiliary_addresses(env):
    """Mark as pickup locations those delivery addresses of partners that match with the
    address data of the pickup locations. This is because this version has a patch for
    avoiding to show that auto-created addresses into the checkout form, which wasn't
    available in 18.

    More info at https://github.com/odoo/odoo/commit/1d24fc854fbb25fbf979f14ecc6a6507fba

    Meanwhile, in 18, it was fixed through OPW putting the record as archived:

    https://github.com/odoo/odoo/pull/242876

    For having consistency, let's put the flag even if they are archived.
    """
    pickup_locations = (
        env["delivery.carrier"]
        .search([("delivery_type", "=", "in_store")])
        .warehouse_ids.partner_id
    )
    for p in pickup_locations:
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE res_partner
            SET is_pickup_location = True
            WHERE
                street = %s,
                city = %s,
                state_id = %s,
                country_id = %s,
                parent_id != False,
                type = 'delivery',
            """,
            (p.street, p.city, p.state_id, p.country_id),
        )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "website_sale_collect", "19.0.1.0/noupdate_changes.xml")
    _mark_pickup_auxiliary_addresses(env)
