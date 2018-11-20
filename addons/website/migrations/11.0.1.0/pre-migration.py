# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

COLUMN_RENAMES = {
    'website': [
        ('social_twitter', None),
        ('social_facebook', None),
        ('social_github', None),
        ('social_linkedin', None),
        ('social_youtube', None),
        ('social_googleplus', None),
    ],
}


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_columns(env.cr, COLUMN_RENAMES)
