# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
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

from osv import fields, osv

class company_header_footer_Setup(osv.osv_memory):
    """
    Insert Information for a company.
    Wizards ask for:
        * A Company with its report header & Footer
        * Fill if Any Changes Needed. 
    """
    _name='wizard.company.header.footer.setup'

    def _get_header2(self,cr,uid,ids):
        return """
        <header>
        <pageTemplate>
        <frame id="first" x1="1.3cm" y1="1.5cm" width="18.4cm" height="26.5cm"/>
        <pageGraphics>
        <fill color="black"/>
        <stroke color="black"/>
        <setFont name="Helvetica" size="8"/>
        <drawString x="1.3cm" y="28.3cm"> [[ formatLang(time.strftime("%Y-%m-%d"), date=True) ]]  [[ time.strftime("%H:%M") ]]</drawString>
        <setFont name="Helvetica-Bold" size="10"/>
        <drawString x="9.8cm" y="28.3cm">[[ company.partner_id.name ]]</drawString>
        <setFont name="Helvetica" size="8"/>
        <drawRightString x="19.7cm" y="28.3cm"><pageNumber/> /  </drawRightString>
        <drawString x="19.8cm" y="28.3cm"><pageCount/></drawString>
        <stroke color="#000000"/>
        <lines>1.3cm 28.1cm 20cm 28.1cm</lines>
        </pageGraphics>
        </pageTemplate>
</header>"""

    def _get_header(self,cr,uid,ids):
        try :
            return tools.file_open(os.path.join('base', 'report', 'corporate_rml_header.rml')).read()
        except:
            return """
    <header>
    <pageTemplate>
        <frame id="first" x1="1.3cm" y1="2.5cm" height="23.0cm" width="19cm"/>
        <pageGraphics>
            <!-- You Logo - Change X,Y,Width and Height -->
        <image x="1.3cm" y="27.6cm" height="40.0" >[[company.logo]]</image>
            <setFont name="Helvetica" size="8"/>
            <fill color="black"/>
            <stroke color="black"/>
            <lines>1.3cm 27.7cm 20cm 27.7cm</lines>

            <drawRightString x="20cm" y="27.8cm">[[ company.rml_header1 ]]</drawRightString>


            <drawString x="1.3cm" y="27.2cm">[[ company.partner_id.name ]]</drawString>
            <drawString x="1.3cm" y="26.8cm">[[ company.partner_id.address and company.partner_id.address[0].street or  '' ]]</drawString>
            <drawString x="1.3cm" y="26.4cm">[[ company.partner_id.address and company.partner_id.address[0].zip or '' ]] [[ company.partner_id.address and company.partner_id.address[0].city or '' ]] - [[ company.partner_id.address and company.partner_id.address[0].country_id and company.partner_id.address[0].country_id.name  or '']]</drawString>
            <drawString x="1.3cm" y="26.0cm">Phone:</drawString>
            <drawRightString x="7cm" y="26.0cm">[[ company.partner_id.address and company.partner_id.address[0].phone or '' ]]</drawRightString>
            <drawString x="1.3cm" y="25.6cm">Mail:</drawString>
            <drawRightString x="7cm" y="25.6cm">[[ company.partner_id.address and company.partner_id.address[0].email or '' ]]</drawRightString>
            <lines>1.3cm 25.5cm 7cm 25.5cm</lines>

            <!--page bottom-->

            <lines>1.2cm 2.15cm 19.9cm 2.15cm</lines>

            <drawCentredString x="10.5cm" y="1.7cm">[[ company.rml_footer1 ]]</drawCentredString>
            <drawCentredString x="10.5cm" y="1.25cm">[[ company.rml_footer2 ]]</drawCentredString>
            <drawCentredString x="10.5cm" y="0.8cm">Company : [[ user.company_id and user.company_id.name ]]</drawCentredString>
            <drawCentredString x="10.5cm" y="0.5cm">Contact : [[ user.name ]] - Page: <pageNumber/></drawCentredString>
        </pageGraphics>
    </pageTemplate>
</header>"""

    _columns = {
        'company_id':fields.many2many('res.company','company_rel', 'c_id', 'c_h_id', 'Companies',required=True),
        'rml_header' : fields.text('RML Header'),
        'rml_header2' : fields.text('RML Internal Header'),

    }
    
    _defaults = {
        'rml_header':_get_header,
        'rml_header2': _get_header2
    }

        
    def action_create(self, cr, uid, ids, context=None):
        wiz_data = self.pool.get('wizard.company.header.footer.setup').read(cr,uid,ids,['company_id','rml_header','rml_header2'])[0]
        if wiz_data['company_id']:
            for c_id in wiz_data['company_id']:
                self.pool.get('res.company').write(cr, uid, [ c_id ], {
                        'rml_header':wiz_data['rml_header'],
                        'rml_header2':wiz_data['rml_header2'],
                    })
            
        return {
                'view_type': 'form',
                "view_mode": 'form',
                'res_model': 'ir.actions.configuration.wizard',
                'type': 'ir.actions.act_window',
                'target':'new',
        }

    def action_cancel(self,cr,uid,ids,conect=None):
        return {
                'view_type': 'form',
                "view_mode": 'form',
                'res_model': 'ir.actions.configuration.wizard',
                'type': 'ir.actions.act_window',
                'target':'new',
        }

company_header_footer_Setup()   


