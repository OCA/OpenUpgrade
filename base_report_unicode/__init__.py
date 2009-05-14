# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2009 Gábor Dukai
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from tools.config import config
import report
import os

def wrap_trml2pdf(method):
    """We have to wrap the original parseString() to modify the rml data
    before it generates the pdf."""
    def convert2TrueType(*args, **argv):
        """This function replaces the type1 font names with their truetype
        substitutes and puts a font registration section at the beginning
        of the rml file. The rml file is acually a string (data)."""
        odata = args[0]
        fontmap = {
            'Times-Roman':                   'DejaVuSerif',
            'Times-BoldItalic':              'DejaVuSerif-BoldItalic',
            'Times-Bold':                    'DejaVuSerif-Bold',
            'Times-Italic':                  'DejaVuSerif-Italic',

            'Helvetica':                     'DejaVuSans',
            'Helvetica-BoldItalic':          'DejaVuSans-BoldOblique',
            'Helvetica-Bold':                'DejaVuSans-Bold',
            'Helvetica-Italic':              'DejaVuSans-Oblique',

            'Courier':                       'DejaVuSansMono',
            'Courier-Bold':                  'DejaVuSansMono-Bold',
            'Courier-BoldItalic':            'DejaVuSansMono-BoldOblique',
            'Courier-Italic':                'DejaVuSansMono-Oblique',

            'Helvetica-ExtraLight':          'DejaVuSans-ExtraLight',

            'TimesCondensed-Roman':          'DejaVuSerifCondensed',
            'TimesCondensed-BoldItalic':     'DejaVuSerifCondensed-BoldItalic',
            'TimesCondensed-Bold':           'DejaVuSerifCondensed-Bold',
            'TimesCondensed-Italic':         'DejaVuSerifCondensed-Italic',

            'HelveticaCondensed':            'DejaVuSansCondensed',
            'HelveticaCondensed-BoldItalic': 'DejaVuSansCondensed-BoldOblique',
            'HelveticaCondensed-Bold':       'DejaVuSansCondensed-Bold',
            'HelveticaCondensed-Italic':     'DejaVuSansCondensed-Oblique',
        }
        i = odata.find('<docinit>')
        if i == -1:
            i = odata.find('<document')
            i = odata.find('>', i)
            i += 1
            starttag = '\n<docinit>\n'
            endtag = '</docinit>'
        else:
            i = i + len('<docinit>')
            starttag = ''
            endtag = ''
        data = odata[:i] + starttag
        adp = os.path.abspath(config['addons_path'])
        for new in fontmap.itervalues():
            fntp = os.path.normcase(os.path.join(adp, 'base_report_unicode', 'fonts', new))
            data += '    <registerFont fontName="' + new + '" fontFile="' + fntp + '.ttf"/>\n'
        data += endtag + odata[i:]
        for  old, new in fontmap.iteritems():
            data = data.replace(old, new)
        return method(data, args[1:] if len(args) > 2 else args[1], **argv)
    return convert2TrueType

report.render.rml2pdf.parseString = wrap_trml2pdf(report.render.rml2pdf.parseString)

report.render.rml2pdf.parseNode = wrap_trml2pdf(report.render.rml2pdf.parseNode)