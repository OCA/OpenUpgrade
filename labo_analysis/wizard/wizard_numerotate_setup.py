##############################################################################
#
# Copyright (c) 2004 TINY SPRL. (http://tiny.be) All Rights Reserved.
#                    Fabien Pinckaers <fp@tiny.Be>
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

import wizard
import netsvc
import pooler
import sql_db
import time

numerotate_form_cont = '''<?xml version="1.0"?>
<form title="%s">
    <field name="start_number" string="%s"/>
    <field name="last_number" string="%s"/>
    <field name="setup_id1" string="%s"/>
</form>''' % ('Continuous Numerotation','First Number', 'Last Number', 'Setup Page')



numerotate_form_alpha = '''<?xml version="1.0"?>
<form title="%s">
    <field name="start_alpha" string="%s"/>
    <field name="last_alpha" string="%s"/>
</form>''' % ('Numerotation Alpha','First Number', 'Last Number')
#    <field name="run" string="%s"/>

numerotate_fields_alpha = {
    'start_alpha': {'string':'First Number', 'type':'char', 'required':True},
    'last_alpha': {'string':'Last Number', 'type':'char', 'required':True},
}
#    'run': {'string':'Run', 'type':'char', 'required':True},

numerotate_fields_cont = {
    'start_number': {'string':'First Number', 'type':'integer', 'required':True},
    'last_number': {'string':'Last Number', 'type':'integer', 'required':True},
    'setup_id1': {'string':'Setup Page', 'type':'many2one', 'relation': 'analysis.setup'}
}

set_cont = '''<?xml version="1.0"?>
<form title="%s">
    <field name="followsheet_id" string="%s"/>
</form>''' % ('Set Followsheet','Followsheet Page')

set_fields_cont = {
    'followsheet_id': {'string':'Setup Page', 'type':'many2one', 'relation': 'labo.followsheet'}
}


set_cont_plate = '''<?xml version="1.0"?>
<form title="%s">
    <field name="plate_id" string="%s"/>
</form>''' % ('Set Plate Extraction','Extraction Plate')

set_fields_cont_plate = {
    'plate_id': {'string':'Plate', 'type':'many2one', 'relation': 'labo.plate'}
}

num_run_form= '''<?xml version="1.0"?>
                <form title="%s">
                <field name="run" string="%s"/>
                </form>''' % ('Set Run','Run')
num_run_fields={
            'run': {'string':'Run', 'type':'char', 'required':True},
}

def _numerotate_cont(self,cr,uid,data,context={}):
    nbr_s = int(data['form']['start_number'])
    nbr_l = int(data['form']['last_number'])
    refs_ls = pooler.get_pool(cr.dbname).get('labo.sample')
    ref_hist = pooler.get_pool(cr.dbname).get('setup.history')
    refs_as = pooler.get_pool(cr.dbname).get('analysis.setup')
    rec_ids = refs_ls.browse(cr,uid,data['ids'])
    nbr=nbr_s
    for r in rec_ids:
        if  nbr<=nbr_l:
            refs_ls.write(cr,uid,[r.id],{'file_setup':data['form']['setup_id1']})
            nbr+=1    
 #      s_id=refs_as.create(cr,uid, {
 #                          'set_up':data['form']['setup_id'],
 #                          'well': nbr,
 #                          'run_setup':'004'
 #                          })
 #          #                'sample_id1':r.id,
         #   b=refs_ls.write(cr,uid,[r.id],{'file_setup':s_id})
      #  if r.file_setup.set_up:
          #  ids_r=refs_as.search(cr,uid,[('set_up','=',data['form']['setup_id1'])])
          #  ids_a=refs_as.browse(cr,uid,ids_r)
           # id_a=ids_a and ids_a[0]
            t=r.file_setup and r.file_setup.set_up or '' 
            if t:
                a=ref_hist.create(cr,uid,{'sample_id':r.id,
                               'setup_id':data['form']['setup_id1'],
                               'setup_id2':t.id or ''
                })
    return {}


def _set_run(self,cr,uid,data,context={}):
    refs_ls = pooler.get_pool(cr.dbname).get('labo.sample')
    refs_as = pooler.get_pool(cr.dbname).get('analysis.setup')
    rec_ids = refs_ls.browse(cr,uid,data['ids'])
    if not len(rec_ids):
        raise wizard.except_wizard('Error!', 'Please, set the number of the setup page')
    for r in rec_ids:
        if not r.file_setup:
            raise wizard.except_wizard('Error!', 'The sample "%s" has no setup page, please set one"'%(r.progenus_number) )

        s_id=refs_as.write(cr,uid,[r.file_setup.id],{
                            'run_setup':data['form']['run'],
                            })
    return {}

def _set_cont_complex(self,cr,uid,data,context={}):
    def sorter(x, y):
        return cmp(x[1],y[1])
    obj= pooler.get_pool(cr.dbname)
    refs_ls = obj.get('labo.sample')
    dog_ids = obj.get('labo.dog')
    refs_as = obj.get('labo.followsheet')
    rec_ids = refs_ls.browse(cr,uid,data['ids'])
    prog_dict={}
    iter=0
    res=data['form']['followsheet_id']
    for r in rec_ids:
        if r.dog_child and r.dog_child.progenus_number and (not r.dog_child.done_i) and (not r.dog_child.follow_sheet_id):
            prog_dict[r.dog_child.progenus_number]=(r.dog_child.id, r.dog_child.done_i)
        if r.dog_mother and r.dog_mother.progenus_number and not r.dog_mother.done_i and not r.dog_mother.follow_sheet_id:
            prog_dict[r.dog_mother.progenus_number]=(r.dog_mother.id, r.dog_mother.done_i)
        if r.dog_father and r.dog_father.progenus_number and not r.dog_father.done_i and not r.dog_father.follow_sheet_id:
            prog_dict[r.dog_father.progenus_number]=(r.dog_father.id, r.dog_father.done_i)
    i=prog_dict.items()
 #   i.sort(sorter)
    i.sort()
    for r in i:
        if not res:
            dog_ids.write(cr,uid,[r[1][0]],{
                            'follow_sheet_id':res,
                            })
        elif iter > 17:
            follow=obj.get('ir.sequence').get(cr, uid, 'labo.followsheet')
            cr.execute("Insert into labo_followsheet(name, date_f) values ('%s', '%s')"%(follow,time.strftime('%Y-%m-%d') ))
            cr.commit()
            cr.execute("select id from labo_followsheet where name = '%s'"%(follow))
            res=cr.fetchone()
            res= res and res[0] or None
            iter=0
        if not r[1][1]:
            iter+=1
            dog_ids.write(cr,uid,[r[1][0]],{
                            'follow_sheet_id':res,
                            })
    return {}
def _set_cont(self,cr,uid,data,context={}):
    obj= pooler.get_pool(cr.dbname)
    refs_ls = obj.get('labo.sample')
    refs_as = obj.get('labo.followsheet')
    rec_ids = refs_ls.browse(cr,uid,data['ids'])
    iter=0
    res=data['form']['followsheet_id']
    for r in rec_ids:
        if not res:
            if not r.done_i:
                refs_ls.write(cr,uid,[r.id],{
                            'follow_sheet_id':res,
                            })
        elif iter > 18:
            follow=obj.get('ir.sequence').get(cr, uid, 'labo.followsheet')
            cr.execute("Insert into labo_followsheet(name, date_f) values ('%s', '%s')"%(follow,time.strftime('%Y-%m-%d') ))
            cr.commit()
            cr.execute("select id from labo_followsheet where name = '%s'"%(follow))
            res=cr.fetchone()
            res= res and res[0] or None
            follow_id=refs_as.search(cr,uid, [('name','=',follow)])
            follow_id= follow_id and follow_id[0] or None
            iter=0
        if not r.done_i and not r.follow_sheet_id:
            refs_ls.write(cr,uid,[r.id],{
                            'follow_sheet_id':res,
                            })
            iter+=1
    return {}

def _set_cont_plate(self,cr,uid,data,context={}):
    refs_ls = pooler.get_pool(cr.dbname).get('labo.sample')
    ref_hist=pooler.get_pool(cr.dbname).get('plate.history')
    refs_as = pooler.get_pool(cr.dbname).get('labo.plate')
    rec_ids = refs_ls.browse(cr,uid,data['ids'])
    for r in rec_ids:
        if r.plate_id:
            ref_hist.create(cr,uid,{'sample_id':r.id,
                                'plate_id':data['form']['plate_id'],
                                'plate_id2':r.plate_id.id
            })
        refs_ls.write(cr,uid,[r.id],{'plate_id':data['form']['plate_id'],})
    return {}

def _numerotate_alpha(self,cr,uid,data,context={}):
    list_alpha=['A01','B01','C01','D01','E01','F01','G01','H01',
                'A02','B02','C02','D02','E02','F02','G02','H02',
                'A03','B03','C03','D03','E03','F03','G03','H03',
                'A04','B04','C04','D04','E04','F04','G04','H04',
                'A05','B05','C05','D05','E05','F05','G05','H05',
                'A06','B06','C06','D06','E06','F06','G06','H06',
                'A07','B07','C07','D07','E07','F07','G07','H07',
                'A08','B08','C08','D08','E08','F08','G08','H08',
                'A09','B09','C09','D09','E09','F09','G09','H09',
                'A10','B10','C10','D10','E10','F10','G10','H10',
                'A11','B11','C11','D11','E11','F11','G11','H11',
                'A12','B12','C12','D12','E12','F12','G12','H12'
                ]
    st_a=data['form']['start_alpha'].upper()
    la_a=data['form']['last_alpha'].upper()
    
    if st_a not in list_alpha:
        raise wizard.except_wizard('Error!', 'Please, Set the right number to the first number')

    if la_a not in list_alpha:
        raise wizard.except_wizard('Error!', 'Please, Set the right number to the last number ')
    
    obj_ls = pooler.get_pool(cr.dbname).get('labo.sample')
    refs_ls=obj_ls.browse(cr,uid,data['ids'])
    start_at=list_alpha.index(st_a)
    stop_at=list_alpha.index(la_a)
    if stop_at<start_at:
        raise wizard.except_wizard('Error!', 'Please check your numerotation "%s" comes after "%s"'%(st_a,la_a))

    for r in refs_ls:
        if start_at<=stop_at:
            k=obj_ls.write(cr,uid,[r.id],{'num_alpha':list_alpha[start_at]})
        start_at+=1
    return{}


class wiz_set_run(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':num_run_form, 'fields': num_run_fields, 'state':[('end','Exit'),('next_step','Set Run')]}
        },
        'next_step': {
            'actions': [_set_run],
            'result': {'type': 'state', 'state':'end'}
        }
    }
wiz_set_run('set.run')
class wiz_set_followsheet(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':set_cont, 'fields': set_fields_cont, 'state':[('end','Exit'),('next_step','Apply')]}
        },
        'next_step': {
            'actions': [_set_cont],
            'result': {'type': 'state', 'state':'end'}
        }
    }
wiz_set_followsheet('set.followsheet')

class wiz_set_followsheet_c(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':set_cont, 'fields': set_fields_cont, 'state':[('end','Exit'),('next_step','Apply')]}
        },
        'next_step': {
            'actions': [_set_cont_complex],
            'result': {'type': 'state', 'state':'end'}
        }
    }
wiz_set_followsheet_c('set.followsheet.c')
class wiz_set_plate(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':set_cont_plate, 'fields': set_fields_cont_plate, 'state':[('end','Exit'),('next_step_p','Apply')]}
        },
        'next_step_p': {
            'actions': [_set_cont_plate],
            'result': {'type': 'state', 'state':'end'}
        }
    }
wiz_set_plate('set.plate')
class wiz_setup_numerotate(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':numerotate_form_cont, 'fields': numerotate_fields_cont, 'state':[('end','Exit'),('set_number','Numerotation')]}
        },
        'set_number': {
            'actions': [_numerotate_cont],
            'result': {'type': 'state', 'state':'end'}
        }
    }
wiz_setup_numerotate('setup.numerotate')



class wiz_numerotate_alpha(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':numerotate_form_alpha, 'fields': numerotate_fields_alpha, 'state':[('end','Exit'),('set_alpha','Numerotation')]}
        },
        'set_alpha': {
            'actions': [_numerotate_alpha],
            'result': {'type': 'state', 'state':'end'}
        }
    }
wiz_numerotate_alpha('numerotate.alpha')

