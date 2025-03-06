# Copyright 2023 Trần Trường Sơn
# Copyright 2023 Rémy Taymans
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_new_fields = [
    (
        "categ_id",  # Field name
        "stock.valuation.layer",  # Model name
        "stock_valuation_layer",  # Table name
        "many2one",  # Odoo Field type (in lower case)
        False,  # [Optional] SQL type (if custom fields)
        "stock_account",  # Module name
        False,  # [Optional] Default value
    )
]


def _fill_stock_valuation_layer_categ_id(env):
    """Field `categ_id` on stock.valuation.layer is now a stored field."""
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_valuation_layer
        SET categ_id = pt.categ_id
        FROM product_product p
        JOIN product_template pt ON p.product_tmpl_id = pt.id
        WHERE stock_valuation_layer.product_id = p.id;
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.add_fields(env, _new_fields)
    _fill_stock_valuation_layer_categ_id(env)
