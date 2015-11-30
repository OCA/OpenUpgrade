# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2010 - 2014 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

# This module provides simple tools for OpenUpgrade migration, specific for
# the 8.0 -> 9.0 migration. It is kept in later editions to keep all the API
# docs in the latest release.


def migrate_model_tables(cr):
    cr.execute("""SELECT 1 FROM information_schema.columns
                  WHERE table_name='ir_model' AND column_name='transient'
                  """)
    found = cr.fetchone()
    if not found:
        # ir_model needs to be updated
        cr.execute("""ALTER TABLE ir_model
                      ADD COLUMN transient boolean
                      """)

        # we assume ir_model_fields needs fixing too
        cr.execute("""ALTER TABLE ir_model_fields
                      ADD COLUMN help varchar,
                      ADD COLUMN index boolean,
                      ADD COLUMN copy boolean,
                      ADD COLUMN related varchar,
                      ADD COLUMN relation_table varchar,
                      ADD COLUMN column1 varchar,
                      ADD COLUMN column2 varchar,
                      ALTER COLUMN select_level SET DEFAULT '0'
                      """)
        
        # ir_model needs to be updated
        cr.execute("""ALTER TABLE ir_model_constraint
                      ADD COLUMN definition varchar
                      """)
