# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Savoir-faire Linux
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

from openerp.openupgrade import openupgrade

column_drops = [
    ('wiki_wiki', 'tags'),
    ('wiki_wiki', 'minor_edit'),
    ('wiki_wiki', 'review'),
    ('wiki_wiki', 'summary'),
    ('wiki_wiki', 'toc'),
    ('wiki_wiki', 'group_id'),
    ('wiki_wiki', 'section'),
    ('wiki_wiki_history', 'minor_edit'),
]

column_renames = {
    'wiki_wiki': [
        ('text_area', 'content'),
    ],
    'wiki_wiki_history': [
        ('text_area', 'content'),
        ('wiki_id', 'page_id'),
    ],
}

table_renames = [
    ('wiki_wiki', 'document_page'),
    ('wiki_wiki_history', 'document_page_history'),
]

model_renames = [
    ('wiki.wiki', 'document.page'),
]


def precreate_approver_gid(cr):
    """Precreate the 'approver_gid' column"""
    cr.execute("""\
ALTER TABLE document_page ADD COLUMN approver_gid integer;
COMMENT ON COLUMN document_page.approver_gid IS 'Approver group';\
""")
    cr.execute("""\
ALTER TABLE document_page
  ADD CONSTRAINT document_page_approver_gid_fkey FOREIGN KEY (approver_gid)
      REFERENCES res_groups (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE SET NULL;\
""")


def precreate_approval_required(cr):
    """Precreate the 'approver_gid' column"""
    cr.execute("""\
ALTER TABLE document_page ADD COLUMN approval_required boolean;
COMMENT ON COLUMN document_page.approval_required IS 'Require approval';\
""")


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.drop_columns(cr, column_drops)
    openupgrade.rename_columns(cr, column_renames)
    openupgrade.rename_tables(cr, table_renames)
    openupgrade.rename_models(cr, model_renames)
    precreate_approver_gid(cr)
    precreate_approval_required(cr)