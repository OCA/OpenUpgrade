# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# Copyright 2024 Hunki enterprises - Holger Brunn
# Copyright 2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def _preserve_pricelist_order(env):
    """As the order determines which priority to apply the pricelists, we should assure
    that with the new order criteria, everything remains the same, so let's rewrite the
    sequence for not depending on the id.
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE product_pricelist pp
        SET sequence = sub.row_number
        FROM (
            SELECT id, row_number()
            OVER (PARTITION BY True order by sequence, id desc)
            FROM product_pricelist
        ) as sub
        WHERE sub.id = pp.id
        """,
    )


def _remove_if_applicable_base_pricelist(env):
    """As this pricelist may be used by users for adding extra rules, we can't just
    remove it. Let's check the content, and if the pricelist hasn't been touched, then
    try to remove it. If any modification, we just remove the XML-ID.
    """
    pricelist = env.ref("product.list0", False)
    if not pricelist:
        return
    if len(pricelist.item_ids) == 1:
        item = pricelist.item_ids
        if (
            item.compute_price == "formula"
            and item.base == "list_price"
            and item.applied_on == "3_global"
            and item.price_discount == 0
            and item.price_surcharge == 0
        ):
            openupgrade.delete_records_safely_by_xml_id(env, ["product.list0"])
            return
    openupgrade.logged_query(
        env.cr, "DELETE FROM ir_model_date WHERE module = 'product' AND name='list0'"
    )


@openupgrade.migrate()
def migrate(env, version):
    _preserve_pricelist_order(env)
    openupgrade.load_data(env, "product", "17.0.1.2/noupdate_changes.xml")
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO product_document (
            ir_attachment_id, active, create_uid, write_uid, create_date, write_date
        )
        SELECT id, True, create_uid, write_uid, create_date, write_date
        FROM ir_attachment
        WHERE res_model IN ('product.product', 'product.template')
        AND res_field IS NULL
        """,
    )
