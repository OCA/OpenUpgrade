# SPDX-FileCopyrightText: 2023 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # The payment migration script renames provider.acquirer to
    # payment.provider. Assume that that script has already been run.

    # The provider (Selection) field no longer exists. The same information is
    # now in custom_mode.
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE payment_provider
        SET code = 'custom', custom_mode = 'wire_transfer'
        WHERE provider = 'transfer'
        """,
    )
