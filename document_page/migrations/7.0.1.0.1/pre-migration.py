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
from openerp.openupgrade.openupgrade import logged_query

column_drops = [
    ('wiki_wiki', 'tags'),
    ('wiki_wiki', 'minor_edit'),
    ('wiki_wiki', 'review'),
    ('wiki_wiki', 'summary'),
    ('wiki_wiki', 'toc'),
    ('wiki_wiki', 'section'),
    ('wiki_wiki_history', 'minor_edit'),
]

column_renames = {
    'wiki_wiki': [
        ('text_area', 'content'),
    ],
    'wiki_groups': [
        ('template', 'content'),
    ],
    'wiki_wiki_history': [
        ('text_area', 'content'),
        ('wiki_id', 'page_id'),
    ],
}

table_renames = [
    ('wiki_wiki', 'document_page'),
    ('wiki_wiki_history', 'document_page_history'),
    ('wiki_create_menu', 'document_page_create_menu'),
]

model_renames = [
    ('wiki.wiki', 'document.page'),
]


def precreate_type_content(cr):
    """Pre-create the 'type' column with 'category' as the value"""
    logged_query(cr, """\
ALTER TABLE wiki_wiki ADD COLUMN type character varying;
COMMENT ON COLUMN wiki_wiki.type IS 'Type';\
""")
    logged_query(cr, """UPDATE wiki_wiki SET type = 'content';""")


def precreate_combine_wiki_groups_wiki_wiki(cr):
    """Put wiki_wiki content into wiki_groups, then delete wiki_groups, conserve parent_id"""
    logged_query(cr, """ALTER TABLE wiki_wiki ADD COLUMN old_id integer;""")
    logged_query(cr, """\
INSERT INTO wiki_wiki(create_uid, create_date, write_date, name, content, type, old_id)
SELECT create_uid, create_date, write_date, name, content, 'category' AS type, id
FROM wiki_groups
ORDER BY id ASC;""")
    logged_query(cr, """\
UPDATE wiki_wiki w
SET parent_id = (SELECT id FROM wiki_wiki WHERE old_id = w.group_id LIMIT 1)
WHERE group_id IS NOT null;\
""")
    openupgrade.drop_columns(cr, [('wiki_wiki', 'group_id'), ('wiki_wiki', 'old_id')])


def precreate_approver_gid(cr):
    """Pre-create the 'approver_gid' column"""
    logged_query(cr, """\
ALTER TABLE document_page ADD COLUMN approver_gid integer;
COMMENT ON COLUMN document_page.approver_gid IS 'Approver group';\
""")
    logged_query(cr, """\
ALTER TABLE document_page
  ADD CONSTRAINT document_page_approver_gid_fkey FOREIGN KEY (approver_gid)
      REFERENCES res_groups (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE SET NULL;\
""")


def precreate_approval_required(cr):
    """Pre-create the 'approval_required' column"""
    logged_query(cr, """\
ALTER TABLE document_page ADD COLUMN approval_required boolean;
COMMENT ON COLUMN document_page.approval_required IS 'Require approval';\
""")


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.drop_columns(cr, column_drops)
    openupgrade.rename_columns(cr, column_renames)
    precreate_type_content(cr)
    precreate_combine_wiki_groups_wiki_wiki(cr)
    openupgrade.rename_tables(cr, table_renames)
    openupgrade.rename_models(cr, model_renames)
    precreate_approver_gid(cr)
    precreate_approval_required(cr)
    logged_query(cr, """DROP TABLE wiki_wiki_page_open;""")
    logged_query(cr, """DROP TABLE wiki_make_index;""")
    logged_query(cr, """DROP TABLE wiki_groups""")
