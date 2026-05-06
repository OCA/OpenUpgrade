# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def change_default_uom_rounding(env):
    # in 13.0, the default value for the rounding field of these units is set
    # to 0.001 in uom_data.xml. this is removed in 14.0, so it falls back to
    # the default value of the field, which is 0.01. the rounding on these
    # units is reset here to their default value if the value hasn’t change,
    # to match how it would be if the database was created in 14.0, which is
    # what is expected from openupgrade.
    for ref in ("uom.product_uom_unit", "uom.product_uom_kgm"):
        uom = env.ref(ref, raise_if_not_found=False)
        if not uom:
            continue
        if uom.rounding == 0.001:
            uom.rounding = 0.01


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "uom", "14.0.1.0/noupdate_changes.xml")
    change_default_uom_rounding(env)
