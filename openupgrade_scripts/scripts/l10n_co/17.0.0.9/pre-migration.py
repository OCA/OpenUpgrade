from openupgradelib import openupgrade


def _disable_obsolete_taxes(env):
    """IN 17.0, some taxes are gone and need to be disabled"""
    for xmlid in ["l10n_co_tax_3"]:
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
