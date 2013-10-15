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
]

model_renames = [
    ('wiki.wiki', 'document.page'),
    ('wiki.wiki.history', 'document.page.history'),
]


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.drop_columns(cr, column_drops)
    openupgrade.rename_columns(cr, column_renames)
    openupgrade.rename_tables(cr, table_renames)
    openupgrade.rename_models(cr, model_renames)
