# Copyright 2020 Odoo Community Association (OCA)
# Copyright 2020 Opener B.V. <stefan@opener.am>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

import odoo


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


def delete_module_not_exist(env):
    env.cr.execute("SELECT id, name from ir_module_module")
    modules_to_delete = []
    for module in env.cr.dictfetchall():
        info = odoo.modules.module.load_information_from_description_file(
            module["name"]
        )
        if info and info["installable"]:
            continue
        elif module != "studio_customization":
            modules_to_delete.append(module["id"])
    modules_to_delete = env["ir.module.module"].browse(modules_to_delete)
    modules_to_delete.module_uninstall()
    modules_to_delete.sudo().unlink()


@openupgrade.migrate()
def migrate(env, version):
    fix_module_category_parent_id(env)
    # Load noupdate changes
    openupgrade.load_data(env.cr, "base", "14.0.1.3/noupdate_changes.xml")
    delete_module_not_exist(env)
