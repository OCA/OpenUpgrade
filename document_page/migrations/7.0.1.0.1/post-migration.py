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
from openerp import pooler, SUPERUSER_ID
from openerp.openupgrade.openupgrade import logged_query


def rename_model_wiki_groups(cr):
    openupgrade.logged_query(cr, """\
UPDATE ir_model_fields SET relation = 'document.page'
WHERE relation = 'wiki.groups'""")
    openupgrade.logged_query(cr, """\
UPDATE ir_model_data SET model = 'document.page'
WHERE model = 'wiki.groups'""")
    openupgrade.logged_query(cr, """\
DELETE FROM ir_model
WHERE model = 'wiki.groups'""")


def combine_wiki_groups_document_page(cr):
    """Put wiki_groups content into wiki_wiki, then delete wiki_groups, conserve parent_id"""
    logged_query(cr, """ALTER TABLE document_page ADD COLUMN old_id integer;""")
    logged_query(cr, """\
INSERT INTO document_page(create_uid, create_date, write_date, name, content, type, old_id)
SELECT create_uid, create_date, write_date, name, content, 'category' AS type, id
FROM wiki_groups
ORDER BY id ASC;""")
    logged_query(cr, """\
UPDATE document_page w
SET parent_id = (SELECT id FROM document_page WHERE old_id = w.group_id LIMIT 1)
WHERE group_id IS NOT null;\
""")
    logged_query(cr, """\
UPDATE ir_model_data d
SET res_id = (SELECT id FROM document_page WHERE old_id = d.res_id LIMIT 1)
WHERE res_id IS NOT null and model = 'wiki.groups';\
""")
    openupgrade.drop_columns(cr, [('document_page', 'group_id'), ('document_page', 'old_id')])
    rename_model_wiki_groups(cr)


def migrate_wiki_to_html(cr, pool):
    document_page_obj = pool.get('document.page')
    wiky = Wiky()
    logged_query(cr, """\
SELECT id, content
FROM document_page
WHERE content is not NULL;
""")
    for page_line_id, content in cr.fetchall():
        document_page_obj.write(
            cr, SUPERUSER_ID, [page_line_id],
            {'content': wiky.process(content)}
        )


@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    combine_wiki_groups_document_page(cr)
    migrate_wiki_to_html(cr, pool)
    logged_query(cr, """DROP TABLE wiki_wiki_page_open;""")
    logged_query(cr, """DROP TABLE wiki_make_index;""")
    logged_query(cr, """DROP TABLE wiki_create_menu""")
    logged_query(cr, """DROP TABLE wiki_groups""")


##############################################################################
#
#    Wiky.py - Python library to converts Wiki MarkUp language to HTML.
#    Based on Wiki.js by Tanin Na Nakorn
#
#    Copyright © 2013 Sandy Carter <bwrsandman@gmail.com>
#    This work is free. You can redistribute it and/or modify it under the
#    terms of the Creative Commons Attribution 3.0 Unported License.
#    (http://creativecommons.org/licenses/by/3.0/legalcode)
#
##############################################################################

import re

re_h3 = re.compile("^===[^=]+===$")
re_h2 = re.compile("^==[^=]+==$")
re_h1 = re.compile("^=[^=]+=$")
re_indent = re.compile("^:+")
re_hr = re.compile("^-{4}")
re_ul = re.compile("^\*+ ")
re_ol = re.compile("^#+ ")
re_ul_ol = re.compile("^(\*+|#+) ")
re_ul_li = re.compile("^(\*+|##+):? ")
re_ol_li = re.compile("^(\*\*+|#+):? ")
re_ul_ol_li = re.compile("^(\*+|#+):? ")
re_youtube = re.compile("^(https?://)?(www\.)?youtube.com/(watch\?(.*)v=|embed/)([^&]+)")
re_b_i = re.compile("'''''(([^']|([^']('{1,4})?[^']))+)'''''")
re_b = re.compile("'''(([^']|([^'](''?)?[^']))+)'''")
re_i = re.compile("''(([^']|([^']'?[^']))+)''")


class Wiky:
    def __init__(self, link_image=None):
        self.link_image = link_image

    def process(self, wikitext):
        lines = wikitext.split("\n")
        html = ""
        i = 0
        while i < len(lines):
            line = lines[i]
            if re_h3.match(line):
                html += "<h3>%s</h3>" % line[3:-3]
            elif re_h2.match(line):
                html += "<h2>%s</h2>" % line[2:-2]
            elif re_h1.match(line):
                html += "<h1>%s</h1>" % line[1:-1]
            elif re_hr.match(line):
                html += "<hr/>"
            elif re_indent.match(line):
                start = i
                while i < len(lines) and re_indent.match(lines[i]):
                    i += 1
                i -= 1
                html += self.process_indent(lines[start: i + 1])
            elif re_ul.match(line):
                start = i
                while i < len(lines) and re_ul_li.match(lines[i]):
                    i += 1
                i -= 1
                html += self.process_bullet_point(lines[start: i + 1])
            elif re_ol.match(line):
                start = i
                while i < len(lines) and re_ol_li.match(lines[i]):
                    i += 1
                i -= 1
                html += self.process_bullet_point(lines[start: i + 1])
            else:
                html += self.process_normal(line)
            html += "<br/>\n"
            i += 1
        return html

    def process_indent(self, lines):
        html = "\n<dl>\n"
        i = 0
        while i < len(lines):
            line = lines[i]
            html += "<dd>"
            this_count = len(re_indent.match(line).group(0))
            html += self.process_normal(line[this_count:])

            nested_end = i
            j = i + 1
            while j < len(lines):
                nested_count = len(re_indent.match(lines[j]).group(0))
                if nested_count <= this_count:
                    break
                else:
                    nested_end = j
                j += 1

            if nested_end > i:
                html += self.process_indent(lines[i + 1: nested_end + 1])
                i = nested_end

            html += "</dd>\n"
            i += 1
        html += "</dl>\n"
        return html

    def process_bullet_point(self, lines):
        if not len(lines):
            return ""
        html = "<ul>" if lines[0][0] == "*" else "<ol>"
        html += '\n'
        i = 0
        while i < len(lines):
            line = lines[i]
            html += "<li>"
            this_count = len(re_ul_ol.match(line).group(1))
            html += self.process_normal(line[this_count+1:])

            # continue previous with #:
            nested_end = i
            j = i + 1
            while j < len(lines):
                nested_count = len(re_ul_ol_li.match(lines[j]).group(1))
                if nested_count < this_count:
                    break
                elif lines[j][nested_count] == ':':
                    html += "<br/>" + self.process_normal(lines[j][nested_count + 2:])
                    nested_end = j
                else:
                    break
                j += 1
            i = nested_end

            # nested bullet point
            nested_end = i
            j = i + 1
            while j < len(lines):
                nested_count = len(re_ul_ol_li.match(lines[j]).group(1))
                if nested_count <= this_count:
                    break
                else:
                    nested_end = j
                j += 1

            if nested_end > i:
                html += self.process_bullet_point(lines[i + 1: nested_end + 1])
                i = nested_end

            # continue previous with #:
            nested_end = i
            j = i + 1
            while j < len(lines):
                nested_count = len(re_ul_ol_li.match(lines[j]).group(1))
                if nested_count < this_count:
                    break
                elif lines[j][nested_count] == ':':
                    html += self.process_normal(lines[j][nested_count + 2:])
                    nested_end = j
                else:
                    break
                j += 1
            i = nested_end
            html += "</li>\n"
            i += 1
        html += "</ul>" if lines[0][0] == "*" else "</ol>"
        html += '\n'
        return html

    def process_url(self, txt):
        css = ('style="background: url(\"%s\") no-repeat scroll '
               'right center transparent;padding-right: 13px;"'
               % self.link_image) if self.link_image else ''
        try:
            index = txt.index(" ")
            url = txt[:index]
            label = txt[index + 1:]
        except ValueError:
            label = url = txt
        return """<a href="%s" %s>%s</a>""" % (url, css, label)

    @staticmethod
    def process_image(txt):
        try:
            index = txt.index(" ")
            url = txt[:index]
            label = txt[index + 1:]
        except ValueError:
            url = txt
            label = ""
        return '<img src="%s" alt="%s" />' % (url, label)

    @staticmethod
    def process_video(url):
        m = re_youtube.match(url)
        if not m:
            return "<b>%s is an invalid YouTube URL</b>" % url
        url = "http://www.youtube.com/embed/" + m.group(5)
        return '<iframe width="480" height="390" src="%s" frameborder="0" allowfullscreen=""></iframe>' % url

    def process_normal(self, wikitext):
        # Image
        while True:
            try:
                index = wikitext.index("[[File:")
                end_index = wikitext.index("]]", index + 7)
                wikitext = (wikitext[:index] +
                            self.process_image(wikitext[index + 7:end_index]) +
                            wikitext[end_index + 2:])
            except ValueError:
                break

        # Video
        while True:
            try:
                index = wikitext.index("[[Video:")
                end_index = wikitext.index("]]", index + 8)
                wikitext = (wikitext[:index] +
                            self.process_video(wikitext[index+8:end_index]) +
                            wikitext[end_index + 2:])
            except ValueError:
                break

        # URL
        for protocol in ["http", "ftp", "news"]:
            end_index = -1
            while True:
                try:
                    index = wikitext.index("[%s://" % protocol, end_index + 1)
                    end_index = wikitext.index("]", index + len(protocol) + 4)
                    wikitext = (wikitext[:index] +
                                self.process_url(wikitext[index+1:end_index]) +
                                wikitext[end_index+1:])
                except ValueError:
                    break

        # Bold, Italics, Emphasis
        wikitext = re_b_i.sub("<b><i>\1</i></b>", wikitext)
        wikitext = re_b.sub("<b>\1</b>", wikitext)
        wikitext = re_i.sub("<i>\1</i>", wikitext)

        return wikitext
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
