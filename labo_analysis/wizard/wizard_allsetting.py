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

req_form_cont = '''<?xml version="1.0"?>
<form title="%s">
    <field name="req" string="%s" domain="[('type_id.code','like','')]" context="{'isdog':'True'}" />
</form>''' % ('Set request', 'Set request')


req_fields_cont = {
    'req': {'string':'Request', 'type':'many2one', 'relation':'labo.analysis.request',
},
}


progenus_fields_cont_1={}
progenus_form_cont_1 = """<?xml version="1.0"?>
<form string="Set Progenus Number">
     <separator string="Set Progenus Number" colspan="4"/>
     <newline/>
</form>
"""

state_form_cont = '''<?xml version="1.0"?>
<form title="%s">
    <field name="state" string="%s"/>
</form>''' % ('Set state', 'State to set')


state_fields_cont = {
    'state': {'string':'State', 'type':'selection', 'selection': [('ko','zero(0)'), ('ok','Analysis OK(1)'),('no_substance','No substance(2)'),('faulty_substance','Faulty Substance(3)'),('incoming_res','Incoming results(4)'), ('exist','Already existing(5)'),('unrealized','Analysis Unrealized(6)'), ('nc','To Reanalise(7)')]},
}

state_fields_req={
    'state': {'string':'State', 'type':'selection', 'selection':[('draft','Draft'), ('running','Running'),('closed','Close'),('cancel','Cancel')]},
    }

daterec_form_cont = '''<?xml version="1.0"?>
<form title="%s">
    <field name="date_rec" string="%s"/>
</form>''' % ('Set date', 'Date to set')

datebeg_form_cont = '''<?xml version="1.0"?>
<form title="%s">
    <field name="date_begin" string="%s"/>
</form>''' % ('Set date', 'Date to set')

datebeg_fields_cont = {
    'date_begin': {'string':'Sending Date', 'type':'date'},
}

daterec_fields_cont = {
    'date_rec': {'string':'Reception Date', 'type':'date'},
}
date_form_cont = '''<?xml version="1.0"?>
<form title="%s">
    <field name="date_clo" string="%s"/>
</form>''' % ('Set date', 'Date to set')


date_fields_cont = {
    'date_clo': {'string':'Closing Date', 'type':'date'},
}


date_form_cont2 = '''<?xml version="1.0"?>
<form title="%s">
    <field name="date_planned" string="%s"/>
</form>''' % ('Set date', 'Date to set')


date_fields_cont2 = {
    'date_planned': {'string':'Planned Date', 'type':'date'},
}


date_limit_form_dog = '''<?xml version="1.0"?>
<form title="%s">
    <field name="date_limit" string="%s"/>
</form>''' % ('Set date', 'Date to set')


date_limit_fields_dog = {
    'date_limit': {'string':'Date Limit', 'type':'date'},
}

date_closing_form_dog = '''<?xml version="1.0"?>
<form title="%s">
    <field name="date_closing" string="%s"/>
</form>''' % ('Set date', 'Date to set')


date_closing_fields_dog = {
    'date_closing': {'string':'Closing date', 'type':'date'},
}

date_eff_form_dog = '''<?xml version="1.0"?>
<form title="%s">
    <field name="date_eff" string="%s"/>
</form>''' % ('Set date', 'Date to set')


date_eff_fields_dog = {
    'date_eff': {'string':'Sample Arrival Date', 'type':'date'},
}

date_reception_form_dog = '''<?xml version="1.0"?>
<form title="%s">
    <field name="date_reception" string="%s"/>
</form>''' % ('Set date', 'Date to set')


date_reception_fields_dog = {
    'date_reception': {'string':'Effective reception date', 'type':'date'},
}

nc_reanalyse_form_dog = '''<?xml version="1.0"?>
<form title="%s">
    <field name="nc_reanalyse" string="%s"/>
</form>''' % ('Set NC reanalyse', 'NC reanalyse to set')


nc_reanalyse_fields_dog = {
    'nc_reanalyse': {'string':'NC reanalyse', 'type':'boolean'},
}

final_c_form_dog = '''<?xml version="1.0"?>
<form title="%s">
    <field name="final_c" string="%s"/>
</form>''' % ('Set Final conformity', 'Final conformity to set')


final_c_fields_dog = {
    'final_c': {'string':'Final conformity', 'type':'boolean'},
}

nc_gle_form_dog = '''<?xml version="1.0"?>
<form title="%s">
    <field name="nc_gle" string="%s"/>
</form>''' % ('Set NC General', 'NC General to set')


nc_gle_fields_dog = {
    'nc_gle': {'string':'NC General', 'type':'boolean'},
}

tag_done_form_dog = '''<?xml version="1.0"?>
<form title="%s">
    <field name="v_tag" string="%s"/>
</form>''' % ('Set Tag Done', 'Set Tag Done')


tag_done_fields_dog = {
    'v_tag': {'string':'tag Done', 'type':'char', 'size':64},
}

card_done_form_dog = '''<?xml version="1.0"?>
<form title="%s">
    <field name="c_done" string="%s"/>
</form>''' % ('Set Card Done', 'Set Card Done')


card_done_fields_dog = {
    'c_done': {'string':'Card Done', 'type':'boolean'},
}

def set_state_req(self,cr,uid,data,context={}):
    obj_requests=pooler.get_pool(cr.dbname).get('labo.analysis.request')
    v_req=obj_requests.browse(cr,uid,data['ids'])
    for i in v_req:
        obj_requests.write(cr,uid,[i.id],{'state':data['form']['state'] })
    return {}

def set_prog_num(self,cr,uid,data,context={}):
    obj_sample=pooler.get_pool(cr.dbname).get('labo.sample')
    v_samples=obj_sample.browse(cr,uid,data['ids'])
    seq_obj=pooler.get_pool(cr.dbname).get('ir.sequence')
    cr.execute("SELECT number_next,code from ir_sequence where name like 'Progenus Number' ")
    res=cr.fetchone()
    for i in v_samples:
        p_num=i.progenus_number
        if not p_num :
            obj_sample.write(cr,uid,[i.id], {'progenus_number': seq_obj.get(cr,uid,res[1]),
                                            'date_reception':time.strftime('%Y-%m-%d') 
                                            })
    return {}

def set_request(self,cr,uid,data,context={}):
    obj_sample=pooler.get_pool(cr.dbname).get('labo.sample')
    v_sample=obj_sample.browse(cr,uid,data['ids'])
    for i in v_sample:
        obj_sample.write(cr,uid,[i.id],{'sample_id':data['form']['req'] })
    return {}

def set_state(self,cr,uid,data,context={}):
    obj_sample=pooler.get_pool(cr.dbname).get('labo.sample')
    v_sample=obj_sample.browse(cr,uid,data['ids'])
    for i in v_sample:
        obj_sample.write(cr,uid,[i.id],{'state':data['form']['state'] })
    return {}

def set_date(self,cr,uid,data,context={}):
    obj_sample=pooler.get_pool(cr.dbname).get('labo.sample')
    v_sample=obj_sample.browse(cr,uid,data['ids'])
    for i in v_sample:
        obj_sample.write(cr,uid,[i.id],{'date_closing':data['form']['date_clo'] })
    return {}

def set_realdate(self,cr,uid,data,context={}):
    obj_sample=pooler.get_pool(cr.dbname).get('labo.sample')
    obj_dog=pooler.get_pool(cr.dbname).get('labo.dog')
    v_sample=obj_sample.browse(cr,uid,data['ids'])
    view_type=v_sample[0].sample_id.type_id.code
    for i in v_sample:
        if view_type!="EMPDOG" and view_type!="EMPDOG_2" and view_type!="EMPCHE":
            obj_sample.write(cr,uid,[i.id],{'date_eff':data['form']['date_clo'] })
        elif view_type=="EMPDOG_2":
            if i.dog_mother:
                obj_dog.write(cr,uid,[i.dog_mother.id],{'date_eff':data['form']['date_clo'] })
            elif i.dog_father:
                obj_dog.write(cr,uid,[i.dog_father.id],{'date_eff':data['form']['date_clo'] })
        elif view_type=="EMPCHE" or view_type=="EMPDOG":
            if i.dog_mother:
                obj_dog.write(cr,uid,[i.dog_mother.id],{'date_eff':data['form']['date_clo'] })
            if i.dog_father:
                obj_dog.write(cr,uid,[i.dog_father.id],{'date_eff':data['form']['date_clo'] })
            if i.dog_child:
                obj_dog.write(cr,uid,[i.dog_child.id],{'date_eff':data['form']['date_clo'] })
    return {}

def set_limitdate(self,cr,uid,data,context={}):
    obj_sample=pooler.get_pool(cr.dbname).get('labo.sample')
    v_sample=obj_sample.browse(cr,uid,data['ids'])
    for i in v_sample:
        obj_sample.write(cr,uid,[i.id],{'date_limit':data['form']['date_clo'] })
    return {}

def set_limitdate_dog(self,cr,uid,data,context={}):
    obj_dog=pooler.get_pool(cr.dbname).get('labo.dog')
    v_dog=obj_dog.browse(cr,uid,data['ids'])
    for i in v_dog:
        obj_dog.write(cr,uid,[i.id],{'date_limit':data['form']['date_limit'] })
    return {}

def set_date_closing_dog(self,cr,uid,data,context={}):
    obj_dog=pooler.get_pool(cr.dbname).get('labo.dog')
    v_dog=obj_dog.browse(cr,uid,data['ids'])
    for i in v_dog:
        obj_dog.write(cr,uid,[i.id],{'date_closing':data['form']['date_closing'] })
    return {}

def set_date_eff_dog(self,cr,uid,data,context={}):
    obj_dog=pooler.get_pool(cr.dbname).get('labo.dog')
    v_dog=obj_dog.browse(cr,uid,data['ids'])
    for i in v_dog:
        obj_dog.write(cr,uid,[i.id],{'date_eff':data['form']['date_eff'] })
    return {}

def set_date_reception_dog(self,cr,uid,data,context={}):
    obj_dog=pooler.get_pool(cr.dbname).get('labo.dog')
    v_dog=obj_dog.browse(cr,uid,data['ids'])
    for i in v_dog:
        obj_dog.write(cr,uid,[i.id],{'date_reception':data['form']['date_reception'] })
    return {}

def set_nc_reanalyse_dog(self,cr,uid,data,context={}):
    obj_dog=pooler.get_pool(cr.dbname).get('labo.dog')
    v_dog=obj_dog.browse(cr,uid,data['ids'])
    for i in v_dog:
        obj_dog.write(cr,uid,[i.id],{'nc_reanalyse':data['form']['nc_reanalyse'] })
    return {}

def set_nc_reanalyse(self,cr,uid,data,context={}):
    obj_dog=pooler.get_pool(cr.dbname).get('labo.sample')
    v_dog=obj_dog.browse(cr,uid,data['ids'])
    for i in v_dog:
        obj_dog.write(cr,uid,[i.id],{'nc_reanalyse':data['form']['nc_reanalyse'] })
    return {}

def set_tag(self,cr,uid,data,context={}):
    obj_dog=pooler.get_pool(cr.dbname).get('labo.dog')
    obj_dog.write(cr,uid,data['ids'],{'v_tag':data['form']['v_tag'] })
    return {}

def set_tag2(self,cr,uid,data,context={}):
    obj_sample=pooler.get_pool(cr.dbname).get('labo.sample')
    obj_sample.write(cr,uid,data['ids'],{'v_tag':data['form']['v_tag'] })
    return {}

def set_card_done(self,cr,uid,data,context={}):
    obj_dog=pooler.get_pool(cr.dbname).get('labo.dog')
    v_dog=obj_dog.browse(cr,uid,data['ids'])
    for i in v_dog:
        obj_dog.write(cr,uid,[i.id],{'c_done':data['form']['c_done'] })
    return {}

def set_nc_gle_dog(self,cr,uid,data,context={}):
    obj_dog=pooler.get_pool(cr.dbname).get('labo.dog')
    v_dog=obj_dog.browse(cr,uid,data['ids'])
    for i in v_dog:
        obj_dog.write(cr,uid,[i.id],{'nc_gle':data['form']['nc_gle'] })
    return {}

def set_nc_gle(self,cr,uid,data,context={}):
    obj_dog=pooler.get_pool(cr.dbname).get('labo.sample')
    v_dog=obj_dog.browse(cr,uid,data['ids'])
    for i in v_dog:
        obj_dog.write(cr,uid,[i.id],{'nc_gle':data['form']['nc_gle'] })
    return {}

def set_final_c_dog(self,cr,uid,data,context={}):
    obj_dog=pooler.get_pool(cr.dbname).get('labo.dog')
    v_dog=obj_dog.browse(cr,uid,data['ids'])
    for i in v_dog:
        obj_dog.write(cr,uid,[i.id],{'final_c':data['form']['final_c'] })
    return {}

def set_final_c(self,cr,uid,data,context={}):
    obj_dog=pooler.get_pool(cr.dbname).get('labo.sample')
    v_dog=obj_dog.browse(cr,uid,data['ids'])
    for i in v_dog:
        obj_dog.write(cr,uid,[i.id],{'final_c':data['form']['final_c'] })
    return {}


def set_recept(self,cr,uid,data,context={}):
    obj_sample=pooler.get_pool(cr.dbname).get('labo.sample')
    v_sample=obj_sample.browse(cr,uid,data['ids'])
    for i in v_sample:
        obj_sample.write(cr,uid,[i.id],{'date_reception':data['form']['date_rec'] })
    return {}

def set_start(self,cr,uid,data,context={}):
    obj_sample=pooler.get_pool(cr.dbname).get('labo.sample')
    v_sample=obj_sample.browse(cr,uid,data['ids'])
    for i in v_sample:
        obj_sample.write(cr,uid,[i.id],{'date_starting':data['form']['date_rec'] })
    return {}

def set_datebeg(self,cr,uid,data,context={}):
    obj_req=pooler.get_pool(cr.dbname).get('labo.analysis.request')
    v_req=obj_req.browse(cr,uid,data['ids'])
    for i in v_req:
        obj_req.write(cr,uid,[i.id],{'begining_date':data['form']['date_begin'] })
    return {}

def set_dateclosing(self,cr,uid,data,context={}):
    obj_req=pooler.get_pool(cr.dbname).get('labo.analysis.request')
    v_req=obj_req.browse(cr,uid,data['ids'])
    for i in v_req:
        obj_req.write(cr,uid,[i.id],{'date_closed':data['form']['date_clo'] })
    return {}

def set_dateplan(self,cr,uid,data,context={}):
    print "ici"
    obj_req=pooler.get_pool(cr.dbname).get('labo.analysis.request')
    v_req=obj_req.browse(cr,uid,data['ids'])
    for i in v_req:
        obj_req.write(cr,uid,[i.id],{'date_planned':data['form']['date_planned'] })
    return {}

class wiz_set_final_c_dog(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':final_c_form_dog, 'fields':final_c_fields_dog , 'state':[('end','Exit'),('final_c','Set Final conformity')]}
        },
        'final_c': {
            'actions': [set_final_c_dog],
            'result': {'type': 'state', 'state':'end'}
        }
    }
wiz_set_final_c_dog('set.final_c')

class wiz_set_final_c(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':final_c_form_dog, 'fields':final_c_fields_dog , 'state':[('end','Exit'),('final_c','Set Final conformity')]}
        },
        'final_c': {
            'actions': [set_final_c],
            'result': {'type': 'state', 'state':'end'}
        }
    }
wiz_set_final_c('set.final_c_s')

class wiz_set_nc_gle(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':nc_gle_form_dog, 'fields':nc_gle_fields_dog , 'state':[('end','Exit'),('nc_gle','Set NC General')]}
        },
        'nc_gle': {
            'actions': [set_nc_gle],
            'result': {'type': 'state', 'state':'end'}
        }
    }
wiz_set_nc_gle('set.nc_gle_s')

class wiz_set_nc_gle_dog(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':nc_gle_form_dog, 'fields':nc_gle_fields_dog , 'state':[('end','Exit'),('nc_gle','Set NC General')]}
        },
        'nc_gle': {
            'actions': [set_nc_gle_dog],
            'result': {'type': 'state', 'state':'end'}
        }
    }
wiz_set_nc_gle_dog('set.nc_gle')

class wiz_set_nc_reanalyse_dog(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':nc_reanalyse_form_dog, 'fields':nc_reanalyse_fields_dog , 'state':[('end','Exit'),('nc_reanalyse','Set NC Reanalyse')]}
        },
        'nc_reanalyse': {
            'actions': [set_nc_reanalyse_dog],
            'result': {'type': 'state', 'state':'end'}
        }
    }
wiz_set_nc_reanalyse_dog('set.nc_reanalyse')

class wiz_set_nc_reanalyse(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':nc_reanalyse_form_dog, 'fields':nc_reanalyse_fields_dog , 'state':[('end','Exit'),('nc_reanalyse','Set NC Reanalyse')]}
        },
        'nc_reanalyse': {
            'actions': [set_nc_reanalyse],
            'result': {'type': 'state', 'state':'end'}
        }
    }
wiz_set_nc_reanalyse('set.nc_reanalyse_s')

class wiz_set_date_reception_dog(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':date_reception_form_dog, 'fields':date_reception_fields_dog , 'state':[('end','Exit'),('set_date_eff','Set date')]}
        },
        'set_date_eff': {
            'actions': [set_date_reception_dog],
            'result': {'type': 'state', 'state':'end'}
        }
    }
wiz_set_date_reception_dog('set.date_reception')

class wiz_set_date_eff_dog(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':date_eff_form_dog, 'fields':date_eff_fields_dog , 'state':[('end','Exit'),('set_date_eff','Set date')]}
        },
        'set_date_eff': {
            'actions': [set_date_eff_dog],
            'result': {'type': 'state', 'state':'end'}
        }
    }
wiz_set_date_eff_dog('set.date_eff')

class wiz_set_date_closing_dog(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':date_closing_form_dog, 'fields':date_closing_fields_dog , 'state':[('end','Exit'),('set_date_closing','Set date')]}
        },
        'set_date_closing': {
            'actions': [set_date_closing_dog],
            'result': {'type': 'state', 'state':'end'}
        }
    }
wiz_set_date_closing_dog('set.date_closing')

class wiz_set_date_limit_dog(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':date_limit_form_dog, 'fields':date_limit_fields_dog , 'state':[('end','Exit'),('set_datelimit','Set date')]}
        },
        'set_datelimit': {
            'actions': [set_limitdate_dog],
            'result': {'type': 'state', 'state':'end'}
        }
    }
wiz_set_date_limit_dog('set.datelimit')


class wiz_set_date_reception(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':daterec_form_cont, 'fields':daterec_fields_cont , 'state':[('end','Exit'),('set_daterec','Set date')]}
        },
        'set_daterec': {
            'actions': [set_recept],
            'result': {'type': 'state', 'state':'end'}
        }
    }
wiz_set_date_reception('set.reception')

class wiz_set_date_starting(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':daterec_form_cont, 'fields':daterec_fields_cont , 'state':[('end','Exit'),('set_datestart','Set date')]}
        },
        'set_datestart': {
            'actions': [set_start],
            'result': {'type': 'state', 'state':'end'}
        }
    }
wiz_set_date_starting('set.starting')

class wiz_set_date_begin(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':datebeg_form_cont, 'fields':datebeg_fields_cont , 'state':[('end','Exit'),('set_datebeg_s','Set date')]}
        },
        'set_datebeg_s': {
            'actions': [set_datebeg],
            'result': {'type': 'state', 'state':'end'}
        }
    }
wiz_set_date_begin('set.begin')

class wiz_set_date_planned(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':date_form_cont2, 'fields':date_fields_cont2 , 'state':[('end','Exit'),('set_date_p','Set date')]}
        },
        'set_date_p': {
            'actions': [set_dateplan],
            'result': {'type': 'state', 'state':'end'}
        }
    }
wiz_set_date_planned('set.date.planned')

class wiz_set_date_closing_request(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':date_form_cont, 'fields':date_fields_cont , 'state':[('end','Exit'),('set_date_c','Set date')]}
        },
        'set_date_c': {
            'actions': [set_dateclosing],
            'result': {'type': 'state', 'state':'end'}
        }
    }
wiz_set_date_closing_request('set.date.req')

class wiz_set_real_date_sample(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':date_form_cont, 'fields':date_fields_cont , 'state':[('end','Exit'),('set_date_re','Set date')]}
        },
        'set_date_re': {
            'actions': [set_realdate],
            'result': {'type': 'state', 'state':'end'}
        }
    }
wiz_set_real_date_sample('set.date.real')


class wiz_set_limit_date_sample(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':date_form_cont, 'fields':date_fields_cont , 'state':[('end','Exit'),('set_date_l','Set date')]}
        },
        'set_date_l': {
            'actions': [set_limitdate],
            'result': {'type': 'state', 'state':'end'}
        }
    }
wiz_set_limit_date_sample('set.date.lim')

class wiz_set_date_closing(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':date_form_cont, 'fields':date_fields_cont , 'state':[('end','Exit'),('set_date','Set date')]}
        },
        'set_date': {
            'actions': [set_date],
            'result': {'type': 'state', 'state':'end'}
        }
    }
wiz_set_date_closing('set.date')

class wiz_set_state(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':state_form_cont, 'fields':state_fields_cont , 'state':[('end','Exit'),('set_state','Set state')]}
        },
        'set_state': {
            'actions': [set_state],
            'result': {'type': 'state', 'state':'end'}
        }
    }
wiz_set_state('set.state')


class wiz_set_request(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':req_form_cont, 'fields':req_fields_cont , 'state':[('end','Exit'),('set_request','Set request')]}
        },
        'set_request': {
            'actions': [set_request],
            'result': {'type': 'state', 'state':'end'}
        }
    }
wiz_set_request('set.request')
class wiz_set_state_req(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':state_form_cont, 'fields':state_fields_req , 'state':[('end','Exit'),('set_state','Set state')]}
        },
        'set_state': {
            'actions': [set_state_req],
            'result': {'type': 'state', 'state':'end'}
        }
    }
wiz_set_state_req('set.state.req')

class wiz_set_progenus_num(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':progenus_form_cont_1, 'fields':progenus_fields_cont_1 , 'state':[('end','Exit'),('set_prog','Set Progenus Number')]}
        },
        'set_prog': {
            'actions': [set_prog_num],
            'result': {'type': 'state', 'state':'end'}
        }
    }
wiz_set_progenus_num('set.prog_num')


class wiz_set_card_done(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':card_done_form_dog, 'fields':card_done_fields_dog , 'state':[('end','Exit'),('card_done','Set Card Done')]}
        },
        'card_done': {
            'actions': [set_card_done],
            'result': {'type': 'state', 'state':'end'}
        }
    }
wiz_set_card_done('set.card_done')

class wiz_set_tag(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':tag_done_form_dog, 'fields':tag_done_fields_dog , 'state':[('end','Exit'),('set_tag_done','Set Tag')]}
        },
        'set_tag_done': {
            'actions': [set_tag],
            'result': {'type': 'state', 'state':'end'}
        }
    }
wiz_set_tag('set.tag_done')
class wiz_set_tag2(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':tag_done_form_dog, 'fields':tag_done_fields_dog , 'state':[('end','Exit'),('set_tag_done2','Set Tag')]}
        },
        'set_tag_done2': {
            'actions': [set_tag2],
            'result': {'type': 'state', 'state':'end'}
        }
    }
wiz_set_tag2('set.tag_done2')
