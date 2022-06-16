from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(
        env.cr,
        [
            ("web.external_layout_background", "web.external_layout_striped"),
            ("web.external_layout_clean", "web.external_layout_bold"),
            ("web.report_layout_background", "web.report_layout_striped"),
            ("web.report_layout_clean", "web.report_layout_bold"),
        ],
    )
