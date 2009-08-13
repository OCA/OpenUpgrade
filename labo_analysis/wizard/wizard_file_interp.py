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
import StringIO
import sys
import time
import os
import string
import errno
import psycopg
import shutil
from datetime import date
import pyExcelerator as xl


_send_form = '''<?xml version="1.0"?>
<form string="Import file .env">
</form>'''

_send_fields = {
}

view_form_finish="""<?xml version="1.0"?>
<form string="Export Analysis Results">
    <image name="gtk-dialog-info" colspan="2"/>
    <group colspan="2" col="4">
        <separator string="Export done" colspan="4"/>
        <field name="data" readonly="1" colspan="3" filename="file_name" />
        <label align="0.0" string="Save this document to a .CSV file and open it with\n your favourite spreadsheet software. The file\n encoding is UTF-8." colspan="4"/>
    </group>
</form>"""
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


class interp_file_simple(wizard.interface):
    def _create_simple(self, cr, uid, data, context):
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
        obj_sample=pooler.get_pool(cr.dbname).get('labo.sample')
        keys=['','']
        sample_ids=obj_sample.browse(cr, uid, data['ids'], context)
        flag_c=''
        mark=[]
        row_lst=[]
        done=[]
        prog_nums=[]
        row_num=1
        file_n=[]
        for col,value in enumerate(keys):
            mysheet.write(0,col,value,header_style)
        for sample in sample_ids:
            cr.execute(" SELECT distinct r.marker_dog, s.create_date  from labo_sample s, dog_allele r where s.progenus_number is not NULL and  "\
                "r.sample_id=s.id and s.progenus_number = '%s' order by s.create_date asc"%(sample.progenus_number))
            prog_mark=cr.fetchall()
            for i in prog_mark:
                if i[0] not in prog_nums:
                    prog_nums.append(i[0])
        keys=keys[0:] + prog_nums[0:]
        for col,value in enumerate(keys):
            mysheet.write(0,col,value,header_style)
        for sample in sample_ids:
            if sample.progenus_number in done:
                continue
            fields=[]
            prog=sample.progenus_number or None
            doss= (sample.sample_id and sample.sample_id.type_id.code or None) + '/' + (sample.sample_id and sample.sample_id.name or None)
            if sample.sample_id and sample.sample_id.name:
                file_n.append(((('/'+sample.sample_id.type_id.code or '') or None ) + (sample.sample_id.name or '')).replace('/',''))
            if sample.progenus_number not in done:
                while len(fields) < len(prog_nums)+2:
                    fields.append('')
                for mark in prog_nums:
                    pos_mark=prog_nums.index(mark)
                  #  cr.execute("select a.allele_dog1, a.allele_dog2, r.name, t.code from dog_allele a, labo_sample s , labo_analysis_request r,"\
                  #              " labo_analysis_type t where t.id=r.type_id and a.sample_id=s.id  and r.id=s.sample_id and s.progenus_number= '%s' "\
                  #              " and a.marker_dog ='%s'"%(sample.progenus_number,mark ))
                    cr.execute("select a.allele_dog1, a.allele_dog2 from dog_allele a, labo_sample s "\
                                "  where a.sample_id=s.id and s.progenus_number= '%s' "\
                                " and a.marker_dog ='%s'"%(sample.progenus_number,mark ))
                    res_all=cr.fetchone()
                    if res_all:
                        flag_c='ok'
                        all_sample=((res_all[0]).zfill(3) or '') +' '+ ((res_all[1]).zfill(3) or '')
                        fields.insert(pos_mark+2,all_sample)
            if flag_c=='ok' and sample.progenus_number not in done:
                done.append(sample.progenus_number)
                fields.__setitem__(0,prog)
                fields.__setitem__(1,doss or None)
                row_lst.append(fields)
                for col,value in enumerate(fields):
                    mysheet.write(row_num,col,value)
                row_num+=1 
        file=StringIO.StringIO()
        out=mydoc.save(file)
        out=base64.encodestring(file.getvalue())

        name=dict([i,0] for i in file_n if i).keys()
        name_f=''
        for i in name:
            name_f+=i +'_'
        file_n=name_f[:-1]
        if len(file_n)>30:
            file_n=file_n[:30] + '.xls'
        else:
            file_n=file_n+'.xls'
        return {'data': out, 'file_name':file_n }

    fields_form_finish={
        'data': {'string':'File', 'type':'binary', 'readonly': True,},
        'file_name':{'string':'File Name', 'type':'char'}
    }
    states={
        'init':{
            'actions': [_create_simple],
            'result': {'type': 'form', 'arch': view_form_finish,
                'fields': fields_form_finish,
                'state': [
                    ('end', 'Close', 'gtk-cancel', True)
                ]
            }
        },
    }

interp_file_simple('file.interp.simple')

class create_interp_file(wizard.interface):
    def _create(self, cr, uid, data, context):
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

        obj_sample=pooler.get_pool(cr.dbname).get('labo.sample')
        sample_ids=obj_sample.browse(cr, uid, data['ids'], context)
        obj_dog = pooler.get_pool(cr.dbname).get('labo.dog')
        keys=['','','']
        fields=[]
        fields1=[]
        fields2=[]
        lst_rows=[]
        mark=[]
        cr.execute("SELECT distinct(r.marker_dog) from dog_allele r, labo_dog d , labo_sample s where r.dog_id1=d.id and  s.id in ("+",".join(map(str,data['ids']))+")  and ( s.dog_mother=d.id or s.dog_father=d.id or s.dog_child=d.id)")
        res=cr.fetchall()
        for r in res:
            mark.append(r[0])
        keys=keys[0:] + mark[0:]
        for col,value in enumerate(keys):
            mysheet.write(0,col,value,header_style)
        file_n=[]
        for sample in sample_ids:
            fields=[]
            fields1=[]
            fields2=[]
            fields3=[]
            flag_m=''
            flag_c=''
            flag_p=''
            if sample.dog_child:
                file_n.append((sample.lp_doss or '')+'_'+str(sample.dog_child.seq or '') or '')
            if sample.dog_mother:
                file_n.append((sample.lp_doss or '')+'_'+str(sample.dog_mother.seq or '') or '')
            if sample.dog_father:
                file_n.append((sample.lp_doss or '')+'_'+str(sample.dog_father.seq or '') or '')
            if sample.dog_child:
                fields=[]
                child=sample.dog_child
                pos=0
                sex_c='C'
                fields.insert(0,sex_c)
                fields.insert(1,sample.lp_doss or None)
                fields.insert(2,child.progenus_number or None)
                for z in mark:
                    while len(fields) < len(mark)+3:
                        fields.append('')
                    pos_mark=mark.index(z)
                    for all in child and child.allele_ids:
                        if all.marker_dog==z:
                            flag_c='ok'
                            all_child=((all.allele_dog1).zfill(3) or '') +' '+ ((all.allele_dog2).zfill(3) or '')
                            fields.insert(pos_mark+3,all_child)
                if flag_c=='ok':
                    lst_rows.append(fields)
            if sample.dog_mother:
                mother=sample.dog_mother
                sex='M'
                fields1.append(sex)
                fields1.append(sample.lp_doss or '')
                fields1.append(mother.progenus_number or '')
                for z in mark:
                    while len(fields1) < len(mark)+3:
                        fields1.append('')
                    pos_mark=mark.index(z)
                    for all in mother and mother.allele_ids:
                        if all.marker_dog==z:
                            flag_m='ok'
                            all_mother=((all.allele_dog1).zfill(3) or '') +' '+ ((all.allele_dog2).zfill(3) or '')
                            fields1.insert(pos_mark+3,all_mother)
                if flag_m=='ok':
                    lst_rows.append(fields1)
            if sample.dog_father:
                fields2=[]
                father=sample.dog_father
                sex='P'
                fields2.append(sex)
                fields2.append(sample.lp_doss or '')
                fields2.append(father.progenus_number or '')
                for z in mark:
                    while len(fields2) < len(mark)+3:
                        fields2.append('')
                   # pos_mark=mark.index(z)
                    for all in father and father.allele_ids:
                        if all.marker_dog==z:
                            pos_mark=mark.index(z)
                            flag_p='ok'
                            all_father=((all.allele_dog1).zfill(3) or '') +' '+ ((all.allele_dog2).zfill(3) or '')
                            fields2.insert(pos_mark+3,all_father)
                if flag_p=='ok':
                    lst_rows.append(fields2)
            lst_rows.append(fields3)
        for row_num,row_values in enumerate(lst_rows):
            row_num+=1 #start at row 1
            row_values = [x.decode('utf8') for x in row_values if x]
            for col,value in enumerate(row_values):
                #normal row
                mysheet.write(row_num,col,value)
        file=StringIO.StringIO()
        out=mydoc.save(file)
        out=base64.encodestring(file.getvalue())

        name=dict([i,0] for i in file_n if i).keys()
        name_f=''
        for i in name:
            name_f+=i +'_'
        file_n=name_f[:-1]# + '.csv'
        if len(file_n)>30:
            file_n=file_n[:30] + '.xls'
        else:
            file_n=file_n+'.xls'
        return {'data': out, 'file_name':file_n}
        return {}

    fields_form_finish={
        'data': {'string':'File', 'type':'binary', 'readonly': True,},
        'file_name':{'string':'File Name', 'type':'char'}
    }
    states={
        'init':{
            'actions': [_create],
            'result': {'type': 'form', 'arch': view_form_finish,
                'fields': fields_form_finish,
                'state': [
                    ('end', 'Close', 'gtk-cancel', True)
                ]
            }
        },
    }

create_interp_file('file.interp')

