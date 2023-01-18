# Copyright 2020 Odoo Community Association (OCA)
# Copyright 2020 Opener B.V. <stefan@opener.am>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def fix_module_category_parent_id(env):
    # due to renames, we need to correct the parent_id
    openupgrade.logged_query(
        env.cr,
        """
        WITH wrong AS (
            SELECT imc.id
            FROM ir_module_category imc
            JOIN ir_module_category parent_imc ON parent_imc.id = imc.parent_id
            JOIN ir_model_data imd ON (
                imd.module = 'base' AND
                imd.model = 'ir.module.category' AND imd.res_id = imc.id)
            JOIN ir_model_data parent_imd ON (
                parent_imd.model = 'ir.module.category' AND
                parent_imd.res_id = parent_imc.id)
            WHERE imd.name NOT LIKE (parent_imd.name || '%')
        ), to_update AS (
            SELECT imc.id, max(parent_imd.name) as parent_name
            FROM wrong imc
            JOIN ir_model_data imd ON (
                imd.model = 'ir.module.category' AND imd.res_id = imc.id)
            LEFT JOIN ir_model_data parent_imd ON (
                parent_imd.module = 'base' AND
                parent_imd.model = 'ir.module.category' AND
                parent_imd.id != imd.id AND
                parent_imd.name != 'module_category_' AND
                imd.name LIKE (parent_imd.name || '%'))
            LEFT JOIN ir_module_category parent_imc ON parent_imd.res_id = parent_imc.id
            GROUP BY imc.id
        )
        UPDATE ir_module_category imc
        SET parent_id = parent_imd.res_id
        FROM to_update
        LEFT JOIN ir_model_data parent_imd ON (
            parent_imd.model = 'ir.module.category' AND
            parent_imd.name = to_update.parent_name)
        WHERE to_update.id = imc.id""",
    )


def assign_module_category_parent(env):
    """As these records are created as noupdate=1, we need to manually assign the
    parent categories that are new in v14.
    """
    category_mapping = [
        ("module_category_sales_sales", "module_category_sales"),
        ("module_category_sales_point_of_sale", "module_category_sales"),
        ("module_category_services_project", "module_category_services"),
        ("module_category_services_timesheets", "module_category_services"),
        ("module_category_accounting_accounting", "module_category_accounting"),
        ("module_category_inventory_purchase", "module_category_inventory"),
        ("module_category_inventory_inventory", "module_category_inventory"),
        (
            "module_category_manufacturing_manufacturing",
            "module_category_manufacturing",
        ),
        ("module_category_manufacturing_maintenance", "module_category_manufacturing"),
        ("module_category_website_live_chat", "module_category_website"),
        ("module_category_website_elearning", "module_category_website"),
        ("module_category_website_website", "module_category_website"),
        ("module_category_marketing_events", "module_category_marketing"),
        ("module_category_marketing_email_marketing", "module_category_marketing"),
        ("module_category_marketing_surveys", "module_category_marketing"),
        ("module_category_human_resources_fleet", "module_category_human_resources"),
        ("module_category_human_resources_lunch", "module_category_human_resources"),
        (
            "module_category_human_resources_employees",
            "module_category_human_resources",
        ),
        (
            "module_category_human_resources_contracts",
            "module_category_human_resources",
        ),
        ("module_category_human_resources_time_off", "module_category_human_resources"),
        (
            "module_category_human_resources_recruitment",
            "module_category_human_resources",
        ),
        ("module_category_human_resources_expenses", "module_category_human_resources"),
        (
            "module_category_human_resources_attendances",
            "module_category_human_resources",
        ),
    ]
    for xml_id, parent_xml_id in category_mapping:
        record = env.ref("base." + xml_id, False)
        if record:
            record.parent_id = env.ref("base." + parent_xml_id, False)


def users_should_export(env):
    # maintain same behavior as previous versions
    export_group = env.ref("base.group_allow_export").id
    user_group = env.ref("base.group_user").id
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO res_groups_users_rel (uid, gid)
        SELECT rel.uid, %s
        FROM res_groups_users_rel rel
        WHERE rel.gid = %s
        ON CONFLICT DO NOTHING
        """,
        (export_group, user_group),
    )


@openupgrade.migrate()
def migrate(env, version):
    fix_module_category_parent_id(env)
    assign_module_category_parent(env)
    users_should_export(env)
    # Load noupdate changes
    openupgrade.load_data(env.cr, "base", "14.0.1.3/noupdate_changes.xml")
