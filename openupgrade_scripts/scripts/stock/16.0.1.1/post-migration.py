from openupgradelib import openupgrade

def _handle_stock_picking_backorder_strategy(env):
    # Handle the merge of OCA/stock-logistics-workflow/stock_picking_backorder_strategy
    # feature in odoo/stock V16 module.
    if openupgrade.column_exists(
        env.cr, "stock_picking_type", openupgrade.get_legacy_name("backorder_strategy")
    ):
        openupgrade.map_values(
            env.cr,
            openupgrade.get_legacy_name("backorder_strategy"),
            "create_backorder",
            [
                ("manual", "ask"),
                ("create", "always"),
                ("no_create", "never"),
                ("cancel", "never"),
            ],
            table="stock_picking_type",
        )

@openupgrade.migrate()
def migrate(env, version):
    _handle_stock_picking_backorder_strategy(env)
    openupgrade.load_data(env.cr, "stock", "16.0.1.1/noupdate_changes.xml")
