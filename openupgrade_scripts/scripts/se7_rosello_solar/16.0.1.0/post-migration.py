from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.update_module_names(
        env.cr,
        [
            ("se7_crm_rosello_solar", "se7_rosello_solar"),
            ("se7_sale_line_nomenclature", "se7_rosello_solar"),
            ("se7_partner_sql_code", "se7_rosello_solar"),
            ("se7_rs_project_onedrive", "se7_rosello_solar"),
        ],
        True
    )
