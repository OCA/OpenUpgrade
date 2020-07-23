# Copyright 2020 Tecnativa - Jairo Llopis
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from csv import DictReader
from pathlib import Path

from openupgradelib import openupgrade


def _migrate_account_types(env):
    """Migrate account.type in account.account records.

    When any account.chart.template is applied, the now missing account.type
    records will produce inconsistencies.

    We use here the ``account_type_mapping.csv`` found in this same folder,
    which includes the account.type records that are now deleted from
    ``l10n_es`` (both Odoo core and OCA/l10n-spain versions of the module) and
    maps them to their equivalent in v11 (Odoo core only).

    To protect against accountants creating their own accounts (which is quite
    common), a fallback mapping is also used at the end.
    """
    # Obtain CSV data
    csv_path = str(Path(__file__).parent / "account_type_mapping.csv")
    with open(csv_path) as csv_fd:
        # Apply exact mapping
        for row in DictReader(csv_fd):
            try:
                params = {
                    "code": row["code"],
                    "new_id": env.ref(row["new_xmlid"]).id,
                    "old_id": env.ref(row["old_xmlid"]).id,
                }
            except ValueError:
                continue  # XML-ID not found
            openupgrade.logged_query(
                env.cr,
                """
                UPDATE account_account
                SET user_type_id = %(new_id)s
                WHERE
                    code LIKE %(code)s || '%%' AND
                    user_type_id = %(old_id)s
                """,
                params,
            )
    # Apply fallback mapping
    mapping_data_fallback = (
        ("l10n_es.account_type_capital", "account.data_account_type_equity"),
        (
            "l10n_es.account_type_financieras",
            "account.data_account_type_current_liabilities",
        ),
        (
            "l10n_es.account_type_stock",
            "account.data_account_type_current_assets",
        ),
        (
            "l10n_es.account_type_tax",
            "account.data_account_type_current_assets",
        ),
        (
            "l10n_es.account_type_terceros",
            "account.data_account_type_current_liabilities",
        ),
    )
    for old_xmlid, new_xmlid in mapping_data_fallback:
        try:
            params = {
                "new_id": env.ref(new_xmlid).id,
                "old_id": env.ref(old_xmlid).id,
            }
        except ValueError:
            continue  # XML-ID not found
        openupgrade.logged_query(
            env.cr,
            """
                UPDATE account_account
                SET user_type_id = %(new_id)s
                WHERE user_type_id = %(old_id)s
            """,
            params,
        )
    # Adjust related field according mappings. Actually, we keep the field
    # synced, no matter if changed here, but for the sake of simplicity
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_move_line aml
        SET user_type_id = aa.user_type_id
        FROM account_account aa
        WHERE aa.id = aml.account_id AND
        (aml.user_type_id != aa.user_type_id OR aml.user_type_id IS NULL)"""
    )


def _rename_account_template_xmlids(env):
    """Rename XML-IDs for all the account templates for avoiding errors with
    the cleanup process due to linked old records.
    """
    for old_coa, new_coa in {
        "": "common",
        "_full": "full",
        "_assoc": "assoc",
        "_pymes": "pymes"
    }.items():
        openupgrade.logged_query(
            env.cr, """
            UPDATE ir_model_data
            SET name = regexp_replace(name, %(old_pattern)s, %(new_pattern)s)
            WHERE module = 'l10n_es' AND name ~ %(old_pattern)s
            """ % {
                'old_pattern': r"$$pgc%s_([0-9]*)_child$$" % old_coa,
                'new_pattern': r"$$account_%s_\1$$" % new_coa,
            }
        )


@openupgrade.migrate()
def migrate(env, version):
    _migrate_account_types(env)
    _rename_account_template_xmlids(env)
