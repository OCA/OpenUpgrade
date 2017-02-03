# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade
from openupgradelib import openupgrade_90

attachment_fields = {
    'slide.slide': [
        ('image', None),
        ('image_medium', None),
        ('image_thumb', None),
    ],
}


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    openupgrade_90.convert_binary_field_to_attachment(env, attachment_fields)
