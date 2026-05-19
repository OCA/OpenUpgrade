# Copyright 2026 Tecnativa - Eduardo Ezerouali
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


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.delete_records_safely_by_xml_id(env, _xmlids_to_delete)
