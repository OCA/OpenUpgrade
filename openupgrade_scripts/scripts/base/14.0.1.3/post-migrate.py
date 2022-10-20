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

def run_lovefurniture(env):
    env.cr.execute(
        "SELECT geo_location,openupgrade_7_migrated_to_partner_id FROM res_partner_address "
        "WHERE geo_location IS NOT NULL"
    )

    for geo_location,partner_id in env.cr.fetchall():
        if geo_location and geo_location != '':
            partner = env["res.partner"].browse(partner_id)
            coordinates = geo_location.split('-')
            lat = lng = 0.0
            if len(coordinates)>0:
                try:
                    lat = float(coordinates[0].strip())
                except Exception as e:
                    pass
            if len(coordinates)>1:
                try:
                    lng = float(coordinates[1].strip())
                except Exception as e:
                    pass
            partner.write({'partner_latitude' : lat,'partner_longitude' : lng})



@openupgrade.migrate()
def migrate(env, version):
    fix_module_category_parent_id(env)
    users_should_export(env)
    run_lovefurniture(env)
    # Load noupdate changes
    openupgrade.load_data(env.cr, "base", "14.0.1.3/noupdate_changes.xml")
