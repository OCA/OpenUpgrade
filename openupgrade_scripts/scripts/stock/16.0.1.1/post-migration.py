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
    if env.ref("base.group_user") in env.ref(multi_location_group_xml_id).implied_ids:
        for xml_id in (
            "stock.stock_location_view_tree2_editable",
            "stock.stock_location_view_form_editable",
        ):
            view = (env.ref(xml_id, raise_if_not_found=False),)
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


@openupgrade.migrate()
def migrate(env, version):
    _handle_multi_location_visibility(env)
    _handle_stock_picking_backorder_strategy(env)
    openupgrade.load_data(env.cr, "stock", "16.0.1.1/noupdate_changes.xml")
