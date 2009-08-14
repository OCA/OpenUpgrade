#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: wizard_spam.py 1005 2005-07-25 08:41:42Z nicoe $
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
import binascii
import wizard
import pooler
import tools
import base64
import csv
import string
import StringIO
from time import strftime
import pyExcelerator as xl
import time
_send_form = '''<?xml version="1.0"?>

<form string="Create Card File">
    <field name="data" readonly="1" colspan="4"/>
</form>'''

_send_fields = {
'data': {'string':'File', 'type':'binary', 'readonly': True,},
}

set_date_form="""<?xml version="1.0"?>
<form string="Set Date">
        <field name="date_print" string="Printed Date" colspan="3" />
</form>
"""
set_date_fields = {
'date_print': {'string':'Printed Date', 'type':'date'},
}
view_form_finish="""<?xml version="1.0"?>
<form string="Export Analysis Result">
    <image name="gtk-dialog-info" colspan="2"/>
    <group colspan="2" col="4">
        <separator string="Export done" colspan="4"/>
        <field name="data" readonly="1" colspan="3" filename="file_name" />
        <label align="0.0" string="Save this document to a .CSV file and open it with\n your favorite spreadsheet software." colspan="4"/>
    </group>
</form>"""
_send_fields1 = {
}

class XlsDoc(xl.CompoundDoc.XlsDoc):
    def saveAsStream(self, ostream, stream):
        # 1. Align stream on 0x1000 boundary (and therefore on sector boundary)
        padding = '\x00' * (0x1000 - (len(stream) % 0x1000))
        self.book_stream_len = len(stream) + len(padding)

        self.__build_directory()
        self.__build_sat()
        self.__build_header()

        ostream.write(self.header)
        ostream.write(self.packed_MSAT_1st)
        ostream.write(stream)
        ostream.write(padding)
        ostream.write(self.packed_MSAT_2nd)
        ostream.write(self.packed_SAT)
        ostream.write(self.dir_stream)

class Workbook(xl.Workbook):
    def save(self, stream):
        doc = XlsDoc()
        doc.saveAsStream(stream, self.get_biff_data())

class create_res(wizard.interface):

#        keys={'Sample Name':'Sample Name','Marker':'Marker','Allele1':'Allele1','Allele2':'Allele2'}
       # keys={'Inu055-2': 'Inu055-2', 'Inu055-1': 'Inu055-1', 'Date of birth': 'Date of birth', 'Breed': 'Breed', 'AHTh160-1': 'AHTh160-1', 'AHTh160-2': 'AHTh160-2', 'Inu030-1': 'Inu030-1', 'Inu030-2': 'Inu030-2', 'AHTh171-1': 'AHTh171-1', 'CXX279-1': 'CXX279-1', 'CXX279-2': 'CXX279-2', 'FH2054-1': 'FH2054-1', 'FH2054-2': 'FH2054-2', 'Amelo-1': 'Amelo-1', 'Amelo-2': 'Amelo-2', 'REN162C04-2': 'REN162C04-2', 'REN162C04-1': 'REN162C04-1', 'REN169O18-2': 'REN169O18-2', 'Inra21-2': 'Inra21-2', 'Inra21-1': 'Inra21-1', 'Name': 'Name', 'AHT121-2': 'AHT121-2', 'AHT121-1': 'AHT121-1', 'printed date': 'printed date', 'AHT137-2': 'AHT137-2', 'AHT137-1': 'AHT137-1', 'REN169D001-1': 'REN169D001-1', 'REN169D001-2': 'REN169D001-2', 'REN169O18-1': 'REN169O18-1', 'REN247M23-1': 'REN247M23-1', 'REN247M23-2': 'REN247M23-2', 'FH2848-2': 'FH2848-2', 'Progenus Num': 'Progenus Num', 'Chip': 'Chip', 'AHTh171-2': 'AHTh171-2', 'Inu005-1': 'Inu005-1', 'Inu005-2': 'Inu005-2', 'Sex': 'Sex', 'FH2848-1': 'FH2848-1', 'Tatoo': 'Tatoo', 'AHTk211-2': 'AHTk211-2', 'REN54P11-2': 'REN54P11-2', 'REN54P11-1': 'REN54P11-1', 'AHTk211-1': 'AHTk211-1'}
#                cr.execute("SELECT d.progenus_number,d.race, d.tatoo, d.ship, d.sex, d.birthdate,d.name,r.allele_dog1, r.allele_dog2 "\
#                            "from dog_allele r, labo_dog d where r.dog_id1=d.id and"\
#                            "d.id in ("+",".join(map(str,data['ids']))+") where r.marker_dog='%s' and d.progenus_number='%s'"%(c,dog.progenus_number))
#
    def _create_dog_num(self, cr, uid, data, context):
        #Open new workbook
        mydoc=Workbook()
        #Add a worksheet
        mysheet=mydoc.add_sheet("test")
        #write headers
        header_font=xl.Font() #make a font object
        header_font.bold=True
        header_font.underline=True
        #font needs to be style actually
        header_style = xl.XFStyle(); header_style.font = header_font

        obj_dogs=pooler.get_pool(cr.dbname).get('labo.dog')
        keys=['','']
        dogs_ids=obj_dogs.browse(cr, uid, data['ids'], context)
        buf=StringIO.StringIO()
        keys=['Progenus Num', 'Name', 'Breed', 'Tatoo', 'Chip','Origin' ,'Sex', 'Date of birth', 'printed date', 'AHT121-1', 'AHT121-2', 'AHT137-1', 'AHT137-2', 'AHTh171-1', 'AHTh171-2', 'AHTh260-1', 'AHTh260-2', 'AHTk211-1', 'AHTk211-2','AHTk253-1','AHTk253-2', 'AMELOGENIN-1', 'AMELOGENIN-2', 'CXX279-1', 'CXX279-2', 'FH2054-1', 'FH2054-2', 'FH2848-1', 'FH2848-2', 'Inra21-1', 'Inra21-2', 'Inu005-1', 'Inu005-2', 'Inu030-1', 'Inu030-2', 'Inu055-1', 'Inu055-2', 'REN162C04-1', 'REN162C04-2', 'REN169D001-1', 'REN169D001-2', 'REN169O18-1', 'REN169O18-2', 'REN247M23-1', 'REN247M23-2', 'REN54P11-1', 'REN54P11-2']
        for col,value in enumerate(keys):

            mysheet.write(0,col,value,header_style)
        writer=csv.writer(buf, 'TINY', delimiter='\t', lineterminator='\r\n')
        writer.writerow(keys)
        row_lst = []
        for dog in dogs_ids:
            row=[]

            if dog.allele_ids and not dog.c_done:
	    	obj_dogs.write(cr,uid,[dog.id],{'c_done':True})
                row.append(dog.progenus_number or ' ')
                row.append(((dog.name).decode('utf-8').encode('utf-8')) or ' ')
                row.append(dog.race or ' ')
                row.append(dog.tatoo or ' ')
                row.append(dog.ship or ' ')
                row.append(dog.origin or ' ')
                row.append(dog.sex or ' ')
                row.append(dog.birthdate or ' ')
                row.append(data['form']['date_print'] or ' ')
                for c in keys[9:]:
                    if keys.index(c) % 2 == 0:
                        c=c.split('-')[0]
                        cr.execute("SELECT r.allele_dog1, r.allele_dog2 "\
                            " from dog_allele r, labo_dog d where r.dog_id1 = d.id  and "\
                            " d.id =%d and r.marker_dog ilike '%s' and d.progenus_number='%s'"%(dog.id, c,dog.progenus_number))
                        res=cr.fetchone()
                        row.append(res and res[0] or '')
                        row.append(res and res[1] or '')

                row_lst.append(row)
                writer.writerow(row)
        for row_num,row_values in enumerate(row_lst):
            row_num+=1 #start at row 1
            row_values = [str(x).decode('utf8') for x in row_values]
            for col,value in enumerate(row_values):
                #normal row
                mysheet.write(row_num,col,value)
        file=StringIO.StringIO()
        out=mydoc.save(file)
        out=base64.encodestring(file.getvalue())
     #   buf.close()
        return {'data':out}

    def _create_dog_letters(self, cr, uid, data, context):
        #Open new workbook
        mydoc=Workbook()
        #Add a worksheet
        mysheet=mydoc.add_sheet("test")
        #write headers
        header_font=xl.Font() #make a font object
        header_font.bold=True
        header_font.underline=True
        #font needs to be style actually
        header_style = xl.XFStyle(); header_style.font = header_font


        obj_dogs=pooler.get_pool(cr.dbname).get('labo.dog')
        obj_ln=pooler.get_pool(cr.dbname).get('letters.numbers')
        dogs_ids=obj_dogs.browse(cr, uid, data['ids'], context)
        buf=StringIO.StringIO()
        keys=['Progenus Num', 'Name', 'Breed', 'Tatoo', 'Chip','Origin' ,'Sex', 'Date of birth', 'printed date', 'AHT121-1', 'AHT121-2', 'AHT137-1', 'AHT137-2', 'AHTh171-1', 'AHTh171-2', 'AHTh260-1', 'AHTh260-2', 'AHTk211-1', 'AHTk211-2', 'AHTk253-1','AHTk253-2', 'AMELOGENIN-1', 'AMELOGENIN-2', 'CXX279-1', 'CXX279-2', 'FH2054-1', 'FH2054-2', 'FH2848-1', 'FH2848-2', 'Inra21-1', 'Inra21-2', 'Inu005-1', 'Inu005-2', 'Inu030-1', 'Inu030-2', 'Inu055-1', 'Inu055-2', 'REN162C04-1', 'REN162C04-2', 'REN169D001-1', 'REN169D001-2', 'REN169O18-1', 'REN169O18-2', 'REN247M23-1', 'REN247M23-2', 'REN54P11-1', 'REN54P11-2']

        for col,value in enumerate(keys):
            mysheet.write(0,col,value,header_style)

        writer=csv.writer(buf, 'TINY', delimiter='\t', lineterminator='\r\n')
        writer.writerow(keys)
        row_lst = []
        for dog in dogs_ids:

            row=[]
            if len(dog.allele_ids) and not dog.c_done:
	    	obj_dogs.write(cr,uid,[dog.id],{'c_done':True})
                row.append(dog.progenus_number or ' ')
                row.append(dog.name or ' ')
                row.append(dog.race or ' ')
                row.append(dog.tatoo or ' ')
                row.append(dog.ship or ' ')
                row.append(dog.origin or '')
                row.append(dog.sex or ' ')
                row.append(dog.birthdate or ' ')
                row.append(data['form']['date_print'] or ' ')
                for c in keys[9:]:
                    if keys.index(c)%2==0:
                        c=c.split('-')[0]
                        cr.execute("SELECT r.allele_dog1, r.allele_dog2 "\
                            "from dog_allele r, labo_dog d where r.dog_id1 = d.id  and "\
                            " d.id =%d and r.marker_dog ilike '%s' and d.progenus_number='%s'"%(dog.id, c,dog.progenus_number))
                        res=cr.fetchone()
                        if res and res[0]:
                            ln_ids_0=obj_ln.search(cr,uid,[('name_number','=',res[0]), ('name','ilike', c)])
                            try:
                                a_1=obj_ln.browse(cr,uid,ln_ids_0)
                                row.append(a_1[0].name_letter or ' ')
                            except:
                                raise wizard.except_wizard('Error!', 'The code of the marker %s with the allele %s does not exist in the table'%(c, res[0]))
                        else:
                            row.append(' ')
                        if res and res[1]:
                            ln_ids_1=obj_ln.search(cr,uid,[('name_number','=',res[1]), ('name','ilike', c)])
                            try:
                                a_2=obj_ln.browse(cr,uid,ln_ids_1)
                                row.append(a_2[0].name_letter or ' ')
                            except:
                                raise wizard.except_wizard('Error!', 'The code of the marker %s  with the allele %s does not exist in the table'%(c, res[0]))
                        else:
                            row.append(' ')
                row_lst.append(row)
                writer.writerow(row)
        for row_num,row_values in enumerate(row_lst):
            row_num+=1 #start at row 1
            row_values = [str(x).decode('utf8') for x in row_values]
            for col,value in enumerate(row_values):
                #normal row
                mysheet.write(row_num,col,value)

        file=StringIO.StringIO()
        out=mydoc.save(file)
        out=base64.encodestring(file.getvalue())
        return {'data':out}

    fields_form_finish={
        'data': {'string':'File', 'type':'binary', 'readonly': True,},
        'file_name':{'string':'File Name', 'type':'char'}
    }
    states = {
        'init':{
            'actions': [],
            'result': {'type': 'form',
                'arch': set_date_form,
                'fields': set_date_fields,
                'state': [('end', 'Close'), ('next_f', 'Create Card File:Numerical Format'), ('next_l', 'Create Card File: Letters')]}
        },
        'next_f':{
            'actions': [_create_dog_num],
            'result': {'type': 'form', 'arch': view_form_finish,
                'fields': fields_form_finish,
                'state': [
                    ('end', 'Close', 'gtk-cancel', True)
                ]
            }
        },
        'next_l':{
            'actions': [_create_dog_letters],
            'result': {'type': 'form', 'arch': view_form_finish,
                'fields': fields_form_finish,
                'state': [
                    ('end', 'Close', 'gtk-cancel', True)
                ]
            }
        },

    }
create_res('labo.card')
