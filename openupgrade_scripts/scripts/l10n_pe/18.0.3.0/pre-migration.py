from openupgradelib import openupgrade


def _disable_obsolete_taxes(env):
    """IN 18.0, some taxes are gone and need to be disabled"""
    for xmlid in ["sale_tax_igv_18_included", "purchase_tax_igv_18_included"]:
        imds = env["ir.model.data"].search(
            [
                ("module", "=", "account"),
                ("model", "=", "account.tax"),
                ("name", "=like", f"%_{xmlid}"),
            ]
        )
        taxes = env["account.tax"].browse(imds.mapped("res_id"))
        taxes.active = False


@openupgrade.migrate()
def migrate(env, version):
    _disable_obsolete_taxes(env)
