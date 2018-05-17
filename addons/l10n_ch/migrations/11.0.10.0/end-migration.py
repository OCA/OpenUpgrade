# Copyright 2018 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def remove_noupdate_records(env):
    """Try to remove deleted noupdate records."""
    xml_ids = [
        'l10n_ch.tax_group_tva_0',
        'l10n_ch.tax_group_tva_25',
        'l10n_ch.tax_group_tva_38',
        'l10n_ch.tax_group_tva_8',
    ]
    for xml_id in xml_ids:
        try:
            record = env.ref(xml_id)
            record.unlink()
        except Exception:  # pragma: no cover
            pass


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    remove_noupdate_records(env)
