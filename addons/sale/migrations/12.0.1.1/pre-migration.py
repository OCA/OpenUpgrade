# Copyright 2019 Eficent <http://www.eficent.com>
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_column_copies = {
    'sale_order_line': [
        ('qty_delivered', None, None),
    ],
}

_column_renames = {
    'payment_transaction': [
        ('sale_order_id', None),
    ],
    'sale_order': [
        ('payment_tx_id', None),
    ],
}

_field_renames_order_dates = [
    ('sale.order', 'sale_order', 'commitment_date',
     openupgrade.get_legacy_name('commitment_date')),
    ('sale.order', 'sale_order', 'requested_date', 'commitment_date'),
]


def fill_sale_order_line_sections(cr):
    """It's done here instead of post-migration to avoid
    possible new rows added in the migration"""
    cr.execute(
        "ALTER TABLE sale_order_line ADD COLUMN display_type varchar",
    )
    openupgrade.logged_query(
        cr, """
        UPDATE sale_order_line sol
        SET sequence = sub.rank * 5
        FROM (
            SELECT id, rank()
            OVER (
                PARTITION BY order_id ORDER BY sequence, id
            ) FROM sale_order_line
        ) sub
        WHERE sol.id = sub.id
        """,
    )
    openupgrade.logged_query(
        cr, """
        ALTER TABLE sale_order_line ALTER COLUMN product_id DROP not null
        """,
    )
    openupgrade.logged_query(
        cr, """
        ALTER TABLE sale_order_line ALTER COLUMN product_uom DROP not null
        """,
    )
    openupgrade.logged_query(
        cr, """
        INSERT INTO sale_order_line (order_id, layout_category_id,
            sequence, name, price_unit, product_uom_qty, customer_lead,
            display_type, create_uid, create_date, write_uid, write_date)
        SELECT sol.order_id, sol.layout_category_id,
            min(sol.sequence) -1 as sequence, max(slc.name), 0, 0, 0,
            'line_section', min(sol.create_uid), min(sol.create_date),
            min(sol.write_uid), min(sol.write_date)
        FROM sale_order_line sol
        INNER JOIN sale_layout_category slc ON slc.id = sol.layout_category_id
        GROUP BY order_id, layout_category_id
        ORDER BY order_id, layout_category_id, sequence
        """
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(env.cr, _column_copies)
    if openupgrade.column_exists(env.cr, 'sale_order', 'payment_tx_id'):
        # from sale_payment module
        openupgrade.rename_columns(env.cr, _column_renames)
    if openupgrade.column_exists(env.cr, 'sale_order', 'requested_date'):
        # from sale_order_dates module
        openupgrade.rename_fields(env, _field_renames_order_dates)
    fill_sale_order_line_sections(env.cr)
