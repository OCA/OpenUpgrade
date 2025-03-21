from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.update_module_names(
        env.cr,
        [("se7_dni_company_contact", "se7_h2o2"), ("se7_h2o2_pago_pagare", "se7_h2o2"), ("se7_h2o2_sale", "se7_h2o2")],
        True
    )
