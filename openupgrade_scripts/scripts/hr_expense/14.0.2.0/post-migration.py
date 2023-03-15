# Copyright 2023 ForgeFlow <https://www.forgeflow.com/>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    product = env.ref("product_product_fixed_cost", raise_if_not_found=False)
    if product:
        try:
            product.default_code = False
        except Exception:
            # this means default_code is requited
            product.default_code += "/1"
