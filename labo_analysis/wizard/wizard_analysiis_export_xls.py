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
import types
import pyExcelerator as xl

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

class wizard_export_samples(wizard.interface):

    def _get_file(self, cr, uid, data, context):

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
        row_lst = []

        obj_sample = pooler.get_pool(cr.dbname).get('labo.sample')
        obj_r = pooler.get_pool(cr.dbname).get('labo.analysis.request')
        obj_dog = pooler.get_pool(cr.dbname).get('labo.dog')
        v_sample=obj_sample.browse(cr, uid, data['ids'], context)
        v_r=obj_sample.browse(cr, uid, data['ids'], context)

    #    view_type=v_sample[0].cont
        seq_obj=pooler.get_pool(cr.dbname).get('ir.sequence')
        v_hist = pooler.get_pool(cr.dbname).get('file.history')
        keys = ['LNPRAP','LPSERV','LPDOSS','LPSEQ','LPENUM','LPENOM','LPENO2','LPEADR','LPELOC','LPRACE','LPFNOM','LPFNUM','LPFTAT','LPFPUC','LPFNOR','LPFDTN','LPFRLB','LPFLLB','LPFNLB','LPFNPR','LPMNOM','LPMNUM','LPMTAT','LPMPUC','LPMNOR','LPMDTN','LPMRLB','LPMLLB','LPMNLB','LPMNPR','LPCSEX','LPCTAT','LPCPUC','LPCDTN','LPCNPR','LPCFIL','LPFILE','LPDTRC','LPNOMT']
        view_b=v_r[0]
        view_type= view_b.sample_id.type_id.code
        buf=StringIO.StringIO()

        for col,value in enumerate(keys):
            mysheet.write(0,col,value,header_style)

        writer=csv.writer(buf, 'TINY', delimiter=',',  lineterminator='\n')
        writer.writerow(keys)
        name_f=[]
        last_f1=''
        row=[]
        cr.execute("SELECT number_next,code,id from ir_sequence where name='RCS'")
        res_cr2=cr.fetchone()
        cr.execute("SELECT number_next,code,id from ir_sequence where name='RFC'")
        res_cr1=cr.fetchone()
        seq_t=seq_obj.browse(cr,uid,res_cr1[1])
#        last_f1=seq_obj.get(cr,uid,res_cr1[1]) +'.xls'
        if (view_type=="EMPDOG" or view_type=="EMPCHE") and v_r and v_r[0]:
            for i in v_r:

                row=[]
        	last_f1=seq_obj.get(cr,uid,res_cr1[1]) +'.xls'
                if i.dog_child:# and i.dog_child.v_done2==0:
                    num_req=i.sample_id.type_id.code + '/'+ i.sample_id.name
                    row.append(num_req or '')
                    lp_serv=i.lp_serv or ''
                    row.append(lp_serv)
                    lp_doss=i.lp_doss or ''
                    row.append(lp_doss)
                    seq= i.dog_child and int(i.dog_child.seq)>0 and i.dog_child.seq or ''
                    row.append(seq)
                    elev_id= i.preleveur1_id and i.preleveur1_id.ref or ''
                    row.append(elev_id)
                    elev_name=i.preleveur1_id and i.preleveur1_id.name or ''
                    row.append(elev_name)
                    elev_name2=i.preleveur1_id and i.preleveur1_id.address and i.preleveur1_id.address[0].name or ''
                    row.append(elev_name2)
                    addr=i.preleveur1_id and i.preleveur1_id.address and i.preleveur1_id.address[0].street or ''
                    row.append(addr)
                    loc=i.preleveur1_id and i.preleveur1_id.address and i.preleveur1_id.address[0].city or ''
                    zip=i.preleveur1_id and i.preleveur1_id.address and i.preleveur1_id.address[0].zip or ''
                    row.append(zip + ' ' +loc)
                    race=i.dog_child and i.dog_child.race or ''
                    row.append(race)
                    mother=i.dog_mother and i.dog_mother.name or ''
                    row.append(mother)
                    m_ped=i.dog_mother and i.dog_mother.pedigree or ''
                    row.append(m_ped)
                    m_tat=i.dog_mother and i.dog_mother.tatoo or ''
                    row.append(m_tat)
                    m_ship=i.dog_mother and i.dog_mother.ship or ''
                    row.append(m_ship)
                    m_org=i.dog_mother and i.dog_mother.origin or ''
                    row.append(m_org)
                    m_birth=i.dog_mother and i.dog_mother.birthdate or ''
                    row.append(m_birth)
                    m_labo=i.dog_mother and i.dog_mother.ref_dog or ''
                    row.append(m_labo)
                    m_labo_name=i.dog_mother and i.dog_mother.labo_id and i.dog_mother.labo_id.name or ''
                    row.append(m_labo_name)
                    m_labo_code=i.dog_mother and i.dog_mother.labo_id and i.dog_mother.labo_id.code or ''
                    row.append(m_labo_code)
                    m_prog=i.dog_mother and i.dog_mother.progenus_number or ''
                    row.append(m_prog)
                    father=i.dog_father and i.dog_father.name or ''
                    row.append(father)
                    f_ped=i.dog_father and i.dog_father.pedigree or ''
                    row.append(f_ped)
                    f_tat=i.dog_father and i.dog_father.tatoo or ''
                    row.append(f_tat)
                    f_ship=i.dog_father and i.dog_father.ship or ''
                    row.append(f_ship)
                    f_org=i.dog_father and i.dog_father.origin or ''
                    row.append(f_org)
                    f_birth=i.dog_father and i.dog_father.birthdate or ''
                    row.append(f_birth)
                    f_labo=i.dog_father and i.dog_father.ref_dog or ''
                    row.append(f_labo)
                    f_labo_name=i.dog_father and i.dog_father.labo_id and i.dog_father.labo_id.name or ''
                    row.append(f_labo_name)
                    f_labo_code=i.dog_father and i.dog_father.labo_id and i.dog_father.labo_id.code or ''
                    row.append(f_labo_code)
                    f_prog=i.dog_father and i.dog_father.progenus_number or ''
                    row.append(f_prog)
                    c_sex=i.dog_child and i.dog_child.sex or ''
                    row.append(c_sex)
                    c_tat=i.dog_child and i.dog_child.tatoo or ''
                    row.append(c_tat)
                    c_ship=i.dog_child and i.dog_child.ship or ''
                    row.append(c_ship)
                    c_bth=''
                    if i.dog_child and i.dog_child.birthdate:
                        c_bth= time.strftime('%d/%m/%y', time.strptime(i.dog_child.birthdate, '%Y-%m-%d'))
                    row.append(c_bth)
                    c_prognum=i.dog_child and i.dog_child.progenus_number or ''
                    row.append(c_prognum)
                    res_f=i.res_filiation or ''
                    row.append(res_f)
                    res_lp=i.lp_file or ''
                    row.append(res_lp)
                    res_rd=''
                    if i.date_reception:
                        res_rd= time.strftime('%d%m%y', time.strptime(i.date_reception, '%Y-%m-%d'))
                    row.append(res_rd)
                    res_tat=i.tatooer_id and i.tatooer_id.name or ''
                    row.append(res_tat)
                    print "row", row
                    if i.dog_mother:
                        obj_dog.write(cr,uid,[i.dog_mother.id],{'v_done2':True})
                        v_hist.create(cr,uid,{'dog_id1':i.dog_mother.id,
                                            'name':last_f1,
                                            })
                    if i.dog_father:
                        obj_dog.write(cr,uid,[i.dog_father.id],{'v_done2':True})
                        v_hist.create(cr,uid,{'dog_id1':i.dog_father.id,
                                            'name':last_f1,
                                            })
                    obj_dog.write(cr,uid,[i.dog_child.id],{'v_done2':True})
                    v_hist.create(cr,uid,{'dog_id1':i.dog_child.id,
                                        'name':last_f1,
                                        })
                    row_lst.append(row)
                    print "row lst", row_lst
                    writer.writerow(row)


        elif view_type=="EMPDOG_2":
            last_f1=seq_obj.get(cr,uid,res_cr1[1]) +'.xls'
            for i in v_sample:
                row=[]
                num_req=i.sample_id.type_id.code + '/'+ i.sample_id.name
                last_f1=seq_obj.get(cr,uid,res_cr2[1]) +'.xls'
                row.append(num_req or '')
                lp_serv=i.lp_serv or ''
                row.append(lp_serv)
                lp_doss=i.lp_doss or ''
                row.append(lp_doss)
                if i.dog_mother:
                    seq=i.dog_mother and int(i.dog_mother.seq)>0 and i.dog_mother.seq or ''
                    row.append(seq)
                elif i.dog_father:
                    seq=i.dog_father and int(i.dog_father.seq)>0 and i.dog_father.seq or ''
                    row.append(seq)
                elev_id=i.preleveur1_id and i.preleveur1_id.ref or ''
                row.append(elev_id)
                elev_name= i.preleveur1_id and i.preleveur1_id.name or ''
                row.append(elev_name)
                elev_name2=i.preleveur1_id and i.preleveur1_id.address and i.preleveur1_id.address[0].name or ''
                row.append(elev_name2)
                addr=i.preleveur1_id and i.preleveur1_id.address and i.preleveur1_id.address[0].street or ''
                row.append(addr)
                loc=i.preleveur1_id and i.preleveur1_id.address and i.preleveur1_id.address[0].city or ''
                zip=i.preleveur1_id and i.preleveur1_id.address and i.preleveur1_id.address[0].zip or ''
                row.append(zip + ' ' +loc)
                if i.dog_mother:# and i.dog_mother.v_done2==0:
                    race=i.dog_mother and i.dog_mother.race or ''
                    row.append(race)
                    mother=i.dog_mother and i.dog_mother.name or ''
                    row.append(mother)
                    m_ped=i.dog_mother and i.dog_mother.pedigree or ''
                    row.append(m_ped)
                    m_tat=i.dog_mother and i.dog_mother.tatoo or ''
                    row.append(m_tat)
                    m_ship=i.dog_mother and i.dog_mother.ship or ''
                    row.append(m_ship)
                    m_org=i.dog_mother and i.dog_mother.origin or ''
                    row.append(m_org)
                    m_birth=i.dog_mother and i.dog_mother.birthdate or ''
                    row.append(m_birth)
                    m_labo=i.dog_mother and i.dog_mother.labo_id and i.dog_mother.labo_id.ref or ''
                    row.append(m_labo)
                    m_labo_name=i.dog_mother and i.dog_mother.labo_id and i.dog_mother.labo_id.name or ''
                    row.append(m_labo_name)
                    m_labo_code=i.dog_mother and i.dog_mother.labo_id and i.dog_mother.labo_id.code or ''
                    row.append(m_labo_code)
                    m_prog=i.dog_mother and i.dog_mother.progenus_number or ''
                    row.append(m_prog)
                    while len(row)<len(keys):
                        row.append('')
                    res_rd=''
                    if i.date_reception:
                        res_rd= time.strftime('%d%m%y', time.strptime(i.date_reception, '%Y-%m-%d'))
                    row.__setitem__(37,res_rd)
                    res_tat=i.tatooer_id and i.tatooer_id.name or ''
                    row.__setitem__(38,res_tat)
                    obj_dog.write(cr,uid,[i.dog_mother.id],{'v_done2':True})
                    v_hist.create(cr,uid,{'dog_id1':i.dog_mother.id,
                                            'name':last_f1,
                                            })
                elif i.dog_father:# and i.dog_father.v_done2==0:
                    while len(row)<len(keys):
                        row.append('')
                    father=i.dog_father and i.dog_father.name or ''
                    row.__setitem__(20,father)
                    f_ped=i.dog_father and i.dog_father.pedigree or ''
                    row.__setitem__(21,f_ped)
                    f_tat=i.dog_father and i.dog_father.tatoo or ''
                    row.__setitem__(22,f_tat)
                    f_ship=i.dog_father and i.dog_father.ship or ''
                    row.__setitem__(23,f_ship)
                    f_org=i.dog_father and i.dog_father.origin or ''
                    row.__setitem__(24,f_org)
                    f_birth=i.dog_father and i.dog_father.birthdate or ''
                    row.__setitem__(25,f_birth)
                    f_labo=i.dog_father and i.dog_father.labo_id and i.dog_father.labo_id.ref or ''
                    row.__setitem__(26,f_labo)
                    f_labo_name=i.dog_father and i.dog_father.labo_id and i.dog_father.labo_id.name or ''
                    row.__setitem__(27,f_labo_name)
                    f_labo_code=i.dog_father and i.dog_father.labo_id and i.dog_father.labo_id.code or ''
                    row.__setitem__(28,f_labo_code)
                    f_prog=i.dog_father and i.dog_father.progenus_number or ''
                    row.__setitem__(29,f_prog)
                   # res_f=i.res_filiation or ''
                   # row.insert(30,res_f)
                    res_lp=i.lp_file or ''
                    row.__setitem__(36,res_lp)
                    res_rd=''
                    res_rd=''
                    if i.date_reception:
                        res_rd= time.strftime('%d%m%y', time.strptime(i.date_reception, '%Y-%m-%d'))
                    row.__setitem__(37,res_rd)
                    res_tat=i.tatooer_id and i.tatooer_id.name or ''
                    row.__setitem__(38,res_tat)
                    obj_dog.write(cr,uid,[i.dog_father.id],{'v_done2':True})
                    v_hist.create(cr,uid,{'dog_id1':i.dog_father.id,
                                            'name':last_f1,
                                            })
                row_lst.append(row)
                writer.writerow(row)
        for row_num,row_values in enumerate(row_lst):
                print row_num, row_values
                row_num+=1 #start at row 1
                row_values = [str(x).decode('utf8') for x in row_values]
                for col,value in enumerate(row_values):
                    #normal row
                #    print "ttt",col, value
                    mysheet.write(row_num,col,value)
        file=StringIO.StringIO()
        out=mydoc.save(file)
        out=base64.encodestring(file.getvalue())
#        buf.close()
        return {'data': out , 'file_name':last_f1}

    def _get_file2(self, cr, uid, data, context):
        req_pool = pooler.get_pool(cr.dbname).get('labo.analysis.request')
        sample_ids = []
        if data['model']=='labo.sample':
            sample_ids = data['ids']
        else:
            requests = req_pool.read(cr,uid,data['ids'],['sample_ids'])
            for req in requests:
                sample_ids.extend(req['sample_ids'])
        export_cols = {
           'LNPRAP1':'sample_id/type_id/code',
           'LNPRAP2':'sample_id/name',
           'LPSERV':'lp_serv',
           'LPDOSS':'lp_doss',
           'LPSEQ':'dog_child/seq',
           'LPENUM':'preleveur1_id/ref',
           'LPENOM':'preleveur1_id/name',
           'LPENO2':'preleveur1_id/address/name',
           'LPEADR':'preleveur1_id/address/street',
           'LPELOC':'preleveur1_id/address/city',
           'LPRACE':'dog_child/race',
           'LPFNOM':'dog_mother/name',
           'LPFNUM':'dog_mother/pedigree',
           'LPFTAT':'dog_mother/tatoo',
           'LPFPUC':'dog_mother/ship',
           'LPFNOR':'dog_mother/origin',
           'LPFDTN':'dog_mother/birthdate',
           'LPFRLB':'dog_mother/labo_id/ref',
           'LPFLLB':'dog_mother/labo_id/name',
           'LPFNLB':'dog_mother/labo_id/code',
           'LPFNPR':'dog_mother/progenus_number',
           'LPMNOM':'dog_father/name',
           'LPMNUM':'dog_father/pedigree',
           'LPMTAT':'dog_father/tatoo',
           'LPMPUC':'dog_father/ship',
           'LPMNOR':'dog_father/origin',
           'LPMDTN':'dog_father/birthdate',
           'LPMRLB':'dog_father/labo_id/ref',
           'LPMLLB':'dog_father/labo_id/name',
           'LPMNLB':'dog_father/labo_id/code',
           'LPMNPR':'dog_father/progenus_number',
           'LPCSEX':'dog_child/sex',
           'LPCTAT':'dog_child/tatoo',
           'LPCPUC':'dog_child/ship',
           'LPCDTN':'dog_child/birthdate',
           'LPCNPR':'dog_child/progenus_number',
           'LPCFIL':'res_filiation',
           'LPFILE':'lp_file',
           'LPDTRC':'date_reception',
           'LPNOMT':'tatooer_id/name',
           'VDONE1':'dog_father/v_done2',
           'VDONE2':'dog_mother/v_done2',
           'VDONE3':'dog_child/v_done2',
        }
        keys = ['LNPRAP1','LNPRAP2','LPSERV','LPDOSS','LPSEQ','LPENUM','LPENOM','LPENO2','LPEADR','LPRACE','LPFNOM','LPFNUM','LPFTAT','LPFPUC','LPFNOR','LPFDTN','LPFRLB','LPFLLB','LPFNLB','LPFNPR','LPMNOM','LPMNUM','LPMTAT','LPMPUC','LPMNOR','LPMDTN','LPMRLB','LPMLLB','LPMNLB','LPMNPR','LPCSEX','LPCTAT','LPCPUC','LPCDTN','LPCNPR','LPCFIL','LPFILE','LPDTRC','LPNOMT']
        keys2 = ['LNPRAP1','LNPRAP2','LPSERV','LPDOSS','LPSEQ','LPENUM','LPENOM','LPENO2','LPEADR','LPRACE','LPFNOM','LPFNUM','LPFTAT','LPFPUC','LPFNOR','LPFDTN','LPFRLB','LPFLLB','LPFNLB','LPFNPR','LPMNOM','LPMNUM','LPMTAT','LPMPUC','LPMNOR','LPMDTN','LPMRLB','LPMLLB','LPMNLB','LPMNPR','LPCSEX','LPCTAT','LPCPUC','LPCDTN','LPCNPR','LPCFIL','LPFILE','LPDTRC','LPNOMT','VDONE1','VDONE2','VDONE3']
        vals = []
        list_done=[]
        dict_done1={}
        dict_done2={}
        dict_done3={}
        lo=0
        for k in keys2:
            vals.append(export_cols[k])
        sample_obj=pooler.get_pool(cr.dbname).get('labo.sample')
        result = sample_obj.export_data(cr,uid,sample_ids,vals,context)
        sample_obj.write(cr,uid,data['ids'],{'state_2':'sent'})
        try:
            buf=StringIO.StringIO()
            writer=csv.writer(buf, 'TINY')
            keys = ['LPNRAP'] + keys[2:]
            writer.writerow(keys)
           # for data in result:
              #  data = [data[0] + '/' + data[1]] + data[2:]
              #  row = []
              #  i=0
              #  for d in data:
              #      if type(d)==types.StringType:
              #          if i==36 and d:
              #              date_rec= time.strftime('%d%m%y', time.strptime(d, '%Y-%m-%d'))
              #              row.append(date_rec)
              #          elif i==32 and d:
              #              date_b= time.strftime('%d/%m/%y', time.strptime(d, '%Y-%m-%d'))
              #              row.append(date_b)
              #          else:
              #              row.append(d.replace('\n',' ').replace('\t',' '))
              #      else:
              #          row.append(d)
              #      i+=1
            writer.writerow(row)
            out=base64.encodestring(buf.getvalue())
            buf.close()

            return {'data': out}
        except IOError, (errno, strerror):
            return {}
        return {}

    fields_form_finish={
        'data': {'string':'File', 'type':'binary', 'readonly': True,},
        'file_name':{'string':'File Name', 'type':'char'}
    }
    states={
        'init':{
            'actions': [_get_file],
            'result': {'type': 'form', 'arch': view_form_finish,
                'fields': fields_form_finish,
                'state': [
                    ('end', 'Close', 'gtk-cancel', True)
                ]
            }
        },
    }
wizard_export_samples('labo.analysis.export.xls')
wizard_export_samples('labo.analysis.request.export.samples')
