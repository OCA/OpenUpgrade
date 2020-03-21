# Copyright 2020 Andrii Skrypka
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


field_renames = [
    ('fetchmail.server',
     'fetchmail_server',
     'type', 'server_type'),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, field_renames)
