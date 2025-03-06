# Copyright 2025 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def _partner_fill_vies_valid(env):
    openupgrade.logged_query(
        env.cr,
        """
        WITH check_vies_enabled AS (
            SELECT COUNT(*) AS count FROM res_company WHERE vat_check_vies
        ),
        eu_countries AS (
            SELECT c.code
            FROM res_country c
            JOIN res_country_res_country_group_rel g ON c.id = g.res_country_id
            JOIN res_country_group cg ON g.res_country_group_id = cg.id
            JOIN ir_model_data imd ON cg.id = imd.res_id
            WHERE imd.module = 'base'
                AND imd.name = 'europe'
                AND imd.model = 'res.country.group'
        )
        UPDATE res_partner p
        SET vies_valid = CASE
            WHEN (SELECT count FROM check_vies_enabled) = 0 THEN FALSE
            WHEN LENGTH(p.vat) > 1
                AND (
                    -- Extract VAT prefix
                    -- 1 or 2 characters according to the logic in _split_vat
                    LEFT(p.vat,
                        CASE WHEN SUBSTRING(p.vat, 2, 1) ~ '[A-Za-z]'
                        THEN 2 ELSE 1 END
                    ) IN (SELECT code FROM eu_countries)
                ) THEN TRUE
            ELSE FALSE
        END;
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _partner_fill_vies_valid(env)
