# Copyright 2019 Eficent <http://www.eficent.com>
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_column_renames = {
    'sale_quote_template': [
        ('require_payment', None),
    ],
    'sale_quote_option': [
        ('layout_category_id', None),  # just in case, we save unused value
    ],
}

_field_renames = [
    ('sale.order', 'sale_order', 'template_id', 'sale_order_template_id'),
    ('sale.order', 'sale_order', 'options', 'sale_order_option_ids'),
    ('sale.quote.line', 'sale_quote_line', 'quote_id',
     'sale_order_template_id'),
    ('sale.quote.option', 'sale_quote_option', 'template_id',
     'sale_order_template_id'),
    ('sale.order.line', 'sale_order_line', 'option_line_id',
     'sale_order_option_ids'),
    ('sale.quote.template', 'sale_quote_template', 'options',
     'sale_order_template_option_ids'),
    ('sale.quote.template', 'sale_quote_template', 'quote_line',
     'sale_order_template_line_ids'),
]

_model_renames = [
    ('sale.quote.line', 'sale.order.template.line'),
    ('sale.quote.option', 'sale.order.template.option'),
    ('sale.quote.template', 'sale.order.template'),
]

_table_renames = [
    ('sale_quote_line', 'sale_order_template_line'),
    ('sale_quote_option', 'sale_order_template_option'),
    ('sale_quote_template', 'sale_order_template'),
]


_white_list_fields = {
    'sale.quote.template': (
        "name", "sale_order_template_line_ids", "note",
        "sale_order_template_option_ids", "number_of_days",
        "require_signature", "require_payment", "mail_template_id", "active",
        "id", "display_name", "name", "create_uid", "create_date", "write_uid",
        "write_date", "__last_update"),
    'sale.quote.line': (
        "sequence", "sale_order_template_id", "name", "product_id",
        "price_unit", "discount", "product_uom_qty", "product_uom_id",
        "display_type", "id", "display_name", "create_uid", "create_date",
        "write_uid", "write_date", "__last_update"),
    'sale.quote.option': (
        "sale_order_template_id", "product_id", "price_unit", "discount",
        "uom_id", "quantity", "id", "display_name", "create_uid",
        "create_date", "write_uid", "write_date", "__last_update"),
}

_white_list_models = {
    'sale.quote.template': 'sale_order_template',
    'sale.quote.line': 'sale_order_template_line',
    'sale.quote.option': 'sale_order_template_option',
}


def put_in_correct_module(cr, white_list):
    # avoid ir_model_data_module_name_uniq_index error
    # because the module of this white fields were sale_quotation_builder
    for model in white_list:
        openupgrade.update_module_moved_fields(
            cr, model, white_list[model],
            'sale_quotation_builder', 'sale_management')
        openupgrade.logged_query(
            cr, """
            UPDATE ir_model_data
            SET module = 'sale_management'
            WHERE name = %s""", ('model_' + _white_list_models[model], ),
        )


def fill_sale_order_template_line_sections(cr):
    """It's done here instead of post-migration to avoid
    possible new rows added in the migration"""
    cr.execute(
        "ALTER TABLE sale_order_template_line ADD COLUMN display_type varchar",
    )
    openupgrade.logged_query(
        cr, """
        UPDATE sale_order_template_line sotl
        SET sequence = sub.rank * 5
        FROM (
            SELECT id, rank()
            OVER (
                PARTITION BY sale_order_template_id ORDER BY sequence, id
            ) FROM sale_order_template_line
        ) sub
        WHERE sotl.id = sub.id
        """,
    )
    openupgrade.logged_query(
        cr, """
        ALTER TABLE sale_order_template_line
        ALTER COLUMN product_id DROP not null
        """,
    )
    openupgrade.logged_query(
        cr, """
        ALTER TABLE sale_order_template_line
        ALTER COLUMN product_uom_id DROP not null
        """,
    )
    openupgrade.logged_query(
        cr, """
        INSERT INTO sale_order_template_line (sale_order_template_id,
            layout_category_id, sequence, name, price_unit, product_uom_qty,
            display_type, create_uid, create_date, write_uid, write_date)
        SELECT sotl.sale_order_template_id, sotl.layout_category_id,
            min(sotl.sequence) - 1 as sequence, max(COALESCE(slc.name, ' ')),
            0, 0, 'line_section', min(sotl.create_uid), min(sotl.create_date),
            min(sotl.write_uid), min(sotl.write_date)
        FROM sale_order_template_line sotl
        LEFT JOIN sale_layout_category slc ON slc.id = sotl.layout_category_id
        WHERE sotl.sale_order_template_id IN (
            SELECT sale_order_template_id
            FROM sale_order_template_line
            WHERE layout_category_id IS NOT NULL)
        GROUP BY sale_order_template_id, layout_category_id
        ORDER BY sale_order_template_id, layout_category_id, sequence
        """
    )


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    if openupgrade.table_exists(env.cr, 'sale_quote_line'):
        # from website_quote module
        openupgrade.rename_columns(cr, _column_renames)
        openupgrade.rename_fields(env, _field_renames)
        put_in_correct_module(cr, _white_list_fields)
        openupgrade.rename_models(cr, _model_renames)
        openupgrade.rename_tables(cr, _table_renames)
        fill_sale_order_template_line_sections(cr)
