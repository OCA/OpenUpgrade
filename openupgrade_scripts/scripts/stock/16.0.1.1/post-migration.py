from openupgradelib import openupgrade


def _handle_multi_location_visibility(env):
    """There are certain views that are disabled/enabled according to the multi-location
    security group, as it can be seen in this commit:

    https://github.com/odoo/odoo/blob/8f6c56d0794c54bde0/addons/stock/models/
    res_config_settings.py#L99-L126

    so we need to mimic that behavior in case the group is enabled, as the views exists
    by default with active=True.
    """
    multi_location_group_xml_id = "stock.group_stock_multi_locations"
    internal_user_id = "base.group_user"
    if env.ref(multi_location_group_xml_id) in env.ref(internal_user_id).implied_ids:
        for xml_id in (
            "stock.stock_location_view_tree2_editable",
            "stock.stock_location_view_form_editable",
        ):
            view = env.ref(xml_id, raise_if_not_found=False)
            if view:
                view.active = False


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


def _complete_stock_move_quantity_done_with_orm(env):
    """In pre-migration we left out the moves with lines with different units of
    measure to be treated by the ORM"""
    env.cr.execute(
        """
        SELECT move_id
        FROM stock_move_line
        WHERE state != 'cancel'
        GROUP BY move_id
        HAVING COUNT(DISTINCT product_uom_id) > 1
            AND SUM(qty_done) <> 0
    """
    )
    move_ids = [id for id, *_ in env.cr.fetchall() if id]
    env["stock.move"].browse(move_ids)._quantity_done_compute()


@openupgrade.migrate()
def migrate(env, version):
    _handle_multi_location_visibility(env)
    _handle_stock_picking_backorder_strategy(env)
    openupgrade.load_data(env.cr, "stock", "16.0.1.1/noupdate_changes.xml")
    _complete_stock_move_quantity_done_with_orm(env)
