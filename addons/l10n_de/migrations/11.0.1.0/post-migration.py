# -*- coding: utf-8 -*-
# © 2018 bloopark systems (<http://bloopark.de>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # replace german "other account type" to generic "other account type"
    type_other_de = env.ref('l10n_de.account_type_other')
    type_other = env.ref('account.data_account_type_other_income')

    env.cr.execute("""
        UPDATE account_account
        SET user_type_id = %(other)s
        WHERE user_type_id = %(other_de)s;

        UPDATE account_journal_type_rel
        SET type_id = %(other)s
        WHERE type_id = %(other_de)s;

        UPDATE account_move_line
        SET user_type_id = %(other)s
        WHERE user_type_id = %(other_de)s;

        UPDATE account_account_template
        SET user_type_id = %(other)s
        WHERE user_type_id = %(other_de)s;
    """, {'other_de': type_other_de.id, 'other': type_other.id})

    try:
        with env.cr.savepoint():
            type_other_de.unlink()
    except Exception:
        pass
