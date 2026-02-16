# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def _product_packaging(env):
    """
    Create UOMs corresponding to the previous packaging's qty field,
    reuse existing UOMs
    """
    env.cr.execute("SELECT id, name, qty FROM product_uom")
    for _id, name, qty in env.cr.fetchall():
        product_uom = env["product.uom"].browse(_id)
        uom = product_uom.product_id.uom_id

        all_uoms = uom
        while all_uoms.related_uom_ids - all_uoms:
            all_uoms += all_uoms.related_uom_ids
        while all_uoms.relative_uom_id - all_uoms:
            all_uoms += all_uoms.relative_uom_id
        existing_uom = env["uom.uom"]
        for possible_uom in all_uoms:
            if uom._compute_quantity(qty, possible_uom) == 1:
                existing_uom = possible_uom
                break

        if not existing_uom:
            existing_uom = env["uom.uom"].create(
                {
                    "name": name,
                    "relative_uom_id": uom.id,
                    "relative_factor": qty,
                }
            )

        product_uom.uom_id = existing_uom


@openupgrade.migrate()
def migrate(env, version):
    _product_packaging(env)
