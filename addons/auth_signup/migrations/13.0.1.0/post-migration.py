# Copyright 2020 Andrii Skrypka
# Copyright 2020 Opener B.V. (stefan@opener.amsterdam)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, 'auth_signup', 'migrations/13.0.1.0/noupdate_changes.xml')
