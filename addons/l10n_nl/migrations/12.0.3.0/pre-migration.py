# Copyright 2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def merge_res_country_states(cr):
    openupgrade.logged_query(
        cr, """
        INSERT INTO ir_model_data (module, name, model, res_id, noupdate)
          SELECT 'l10n_nl',
                 CONCAT('state_nl_', LOWER(s.code)),
                 'res.country.state',
                 s.id,
                 false
          FROM res_country_state s
              JOIN res_country c ON s.country_id = c.id
              WHERE c.code LIKE 'NL'
                AND UPPER(s.code) IN ('DR','FL','FR','GE','GR','LI','NB','NH',
                                      'OV','UT','ZE','ZH','BQ1','BQ2','BQ3')
        ON CONFLICT DO NOTHING
        """
    )


def switch_noupdate_records(env):
    openupgrade.set_xml_ids_noupdate_value(
        env,
        "l10n_nl",
        [
            "tag_nl_34",
        ],
        False,
    )


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    switch_noupdate_records(env)
    merge_res_country_states(cr)
