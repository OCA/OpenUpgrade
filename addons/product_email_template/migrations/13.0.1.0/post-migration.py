# Copyright 2024 Le Filament <https://le-filament.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def update_product_template_mail_model(env):
    """
    Mail template model has changed from product.template to account.move in v13
    """
    account_move_model = env["ir.model"].search([("model", "=", "account.move")])
    mail_template_ids = env["product.template"].search(
        [("email_template_id", "!=", False)]
    ).mapped("email_template_id")
    mail_template_ids.filtered(lambda t: t.model == 'product.template').write(
        {"model_id": account_move_model.id}
    )


@openupgrade.migrate()
def migrate(env, version):
    update_product_template_mail_model(env)
