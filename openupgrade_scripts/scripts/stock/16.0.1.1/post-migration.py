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


@openupgrade.migrate()
def migrate(env, version):
    _handle_multi_location_visibility(env)
    openupgrade.load_data(env.cr, "stock", "16.0.1.1/noupdate_changes.xml")
