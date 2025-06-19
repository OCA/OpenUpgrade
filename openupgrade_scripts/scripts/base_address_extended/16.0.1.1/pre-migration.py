# Copyright 2025 Dixmit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_add_fields = [
    (
        "street_name",
        "res.partner",
        "res_partner",
        "char",
        None,
        "base_address_extended",
        None,
    ),
    (
        "street_number",
        "res.partner",
        "res_partner",
        "char",
        None,
        "base_address_extended",
        None,
    ),
    (
        "street_number2",
        "res.partner",
        "res_partner",
        "char",
        None,
        "base_address_extended",
        None,
    ),
]


@openupgrade.migrate()
def migrate(env, _version):
    openupgrade.add_fields(env, _add_fields)
    # We need to use the subquery because the regex is not allowed inside the UPDATE statement
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE res_partner
        SET
            street_name = TRIM(rgx[1]),
            street_number = TRIM(rgx[2]),
            street_number2 = TRIM(rgx[3])
        FROM (
            SELECT
                id,
                regexp_match(street, '^(.*?)(?:\\s([0-9][0-9^\\s]*))?(?: - (.+))?$') AS rgx
            FROM res_partner
            WHERE street IS NOT NULL
        ) AS sub
        WHERE res_partner.id = sub.id;
        """,
    )
