# Copyright 2026 Tecnativa - Eduardo Ezerouali
# Copyright 2026 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from openupgradelib import openupgrade

_xmlids_to_delete = [
    "l10n_es.account_tag_mod390_m104",
    "l10n_es.account_tag_mod390_m230",
    "l10n_es.account_tag_mod390_m232",
    "l10n_es.account_tag_mod390_m773",
    "l10n_es.account_tag_mod390_m774",
    "l10n_es.account_tag_mod390_m775",
    "l10n_es.account_tag_mod390_m776",
]


def _fp_xml_id_renaming(env):
    """In 19.0, this fiscal position has changed its XML-ID. We need to look for all
    the posible occurrences across companies.
    """
    for src, dest in [
        ("fp_nacional", "l10n_es_domestic_fiscal_position"),
    ]:
        imds = env["ir.model.data"].search(
            [
                ("module", "=", "account"),
                ("model", "=", "account.fiscal.position"),
                ("name", "=like", f"%_{src}"),
            ]
        )
        for imd in imds:
            imd.name = imd.name.replace(src, dest)


@openupgrade.migrate()
def migrate(env, version):
    _fp_xml_id_renaming(env)
    openupgrade.delete_records_safely_by_xml_id(env, _xmlids_to_delete)
