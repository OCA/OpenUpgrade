# coding: utf-8
# Copyright (C) 2020 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade
from psycopg2 import ProgrammingError


def _populate_invoice_journal_id(env):
    try:
        # We try to create the new field.
        # It will fail if pos_invoice_journal has been installed
        openupgrade.logged_query(
            env.cr, """
            ALTER TABLE pos_config
            ADD column invoice_journal_id integer;"""
        )
    except ProgrammingError:
        return
    openupgrade.logged_query(
        env.cr, """
        UPDATE pos_config
        SET invoice_journal_id = journal_id;"""
    )


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    _populate_invoice_journal_id(env)
