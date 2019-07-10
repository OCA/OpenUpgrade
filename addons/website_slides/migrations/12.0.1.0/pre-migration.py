# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_field_renames = [
    ('slide.channel', 'slide_channel', 'website_published', 'is_published'),
    ('slide.slide', 'slide_slide', 'website_published', 'is_published'),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _field_renames)
