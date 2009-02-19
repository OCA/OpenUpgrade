import wizard
import pooler
import time
import tools
import os

view_form_profit = """<?xml version="1.0"?>
<form string="Setup">
    <image name="gtk-dialog-info"/>
    <group>
        <separator string="Select a Profile" colspan="2"/>
        <newline/>
        <field align="0.0" name="profile"/>
        <newline/>
        <label string="A profile sets a pre-selection of modules for specific needs. These profiles have been setup to help you discover the different aspects of OpenERP. This is just an overview, we have 300+ available modules." colspan="2" align="0.0"/>
        <newline/>
        <label string="You'll be able to install more modules later through the Administration menu." colspan="2" align="0.0"/>
    </group>
</form>"""

view_form_company = """<?xml version="1.0"?>
<form string="Setup">
    <image name="gtk-dialog-info" colspan="2"/>
    <group>
        <separator string="Define main company" colspan="4"/>
        <newline/>
        <field name="name" align="0.0" colspan="4" required="True"/>
        <newline/>
        <field name="street" align="0.0"/>
        <field name="street2" align="0.0"/>
        <field name="zip" align="0.0"/>
        <field name="city" align="0.0"/>
        <field name="country_id" align="0.0"/>
        <field name="state_id" align="0.0"/>
        <field name="email" align="0.0"/>
        <field name="phone" align="0.0"/>
        <field name="currency" align="0.0"/>
        <field name="vat_no"/>
        <field name="cst_no"/>
        <field name="pan_no"/>
        <field name="sr_tax"/>
        <separator string="Exices Details" colspan="4"/>
        <field name="excise"/>
        <field name="range"/>
        <field name="div"/>

        <separator string="Report header" colspan="4"/>
        <newline/>
        <field name="rml_header1" align="0.0" colspan="4"/>
        <field name="rml_footer1" align="0.0" colspan="4"/>
        <field name="rml_footer2" align="0.0" colspan="4"/>
    </group>
</form>"""

view_form_update = """<?xml version="1.0"?>
<form string="Setup">
    <image name="gtk-dialog-info" colspan="2"/>
    <group>
        <separator string="Summary" colspan="2"/>
        <newline/>
        <field name="profile" align="0.0" readonly="1"/>
        <newline/>
        <field name="name" align="0.0" readonly="1"/>
    </group>
</form>
"""

view_form_finish = """<?xml version="1.0"?>
<form string="Setup">
    <image name="gtk-dialog-info" colspan="2"/>
    <group colspan="2" col="4">
        <separator colspan="4" string="Installation Done"/>
        <label align="0.0" colspan="4" string="Your new database is now fully installed."/>
        <label align="0.0" colspan="4" string="You can start configuring the system or connect directly to the database using the default setup."/>
    </group>
</form>
"""

class voucher_wizard_base_setup(wizard.interface):
    def _get_profiles(self, cr, uid, context):
        module_obj=pooler.get_pool(cr.dbname).get('ir.module.module')
        ids=module_obj.search(cr, uid, [('category_id', '=', 'Profile'),
            ('state', '<>', 'uninstallable')])
        res=[(m.id, m.shortdesc) for m in module_obj.browse(cr, uid, ids, context=context)]
        res.append((-1, 'Minimal Profile'))
        res.sort()
        return res
    
    def _get_company(self, cr, uid, data, context):
        pool=pooler.get_pool(cr.dbname)
        company_obj=pool.get('res.company')
        ids=company_obj.search(cr, uid, [])
        if not ids:
            return {}
        company=company_obj.browse(cr, uid, ids)[0]
        self.fields['name']['default']=company.name
        self.fields['currency']['default']=company.currency_id.id
        serv_pro_id = pooler.get_pool(cr.dbname).get('ir.module.module').search(cr, uid, [('name','=','profile_service')]) or False
        if serv_pro_id:
            return {'profile':serv_pro_id[0]}
        return {}
    
    def _get_states(self, cr, uid, context):
        pool=pooler.get_pool(cr.dbname)
        state_obj=pool.get('res.country.state')
        ids=state_obj.search(cr, uid, [])
        res=[(state.id, state.name) for state in state_obj.browse(cr, uid, ids, context=context)]
        res.append((-1, ''))
        res.sort(lambda x,y: cmp(x[1],y[1]))
        return res
    
    def _get_countries(self, cr, uid, context):
        pool=pooler.get_pool(cr.dbname)
        country_obj=pool.get('res.country')
        ids=country_obj.search(cr, uid, [])
        res=[(country.id, country.name) for country in country_obj.browse(cr, uid, ids, context=context)]
        res.sort(lambda x,y: cmp(x[1],y[1]))
        return res
    
    
    def _get_currency(self, cr, uid, context):
        pool=pooler.get_pool(cr.dbname)
        currency_obj=pool.get('res.currency')
        ids=currency_obj.search(cr, uid, [])
        res=[(currency.id, currency.name) for currency in currency_obj.browse(cr, uid, ids, context=context)]
        res.sort(lambda x,y: cmp(x[1],y[1]))
        return res

    def _update(self, cr, uid, data, context):
        pool=pooler.get_pool(cr.dbname)
        form=data['form']
        if 'profile' in data['form'] and data['form']['profile'] > 0:
            module_obj=pool.get('ir.module.module')
            module_obj.state_update(cr, uid, [data['form']['profile']], 'to install', ['uninstalled'], context)

        company_obj=pool.get('res.company')
        partner_obj=pool.get('res.partner')
        address_obj=pool.get('res.partner.address')
        ids=company_obj.search(cr, uid, [])
        company=company_obj.browse(cr, uid, ids)[0]
        company_obj.write(cr, uid, [company.id], {
                'name': form['name'],
                'rml_header1': form['rml_header1'],
                'rml_footer1': form['rml_footer1'],
                'rml_footer2': form['rml_footer2'],
                'currency_id': form['currency'],
                'logo': form['logo'],
            })
        partner_obj.write(cr, uid, [company.partner_id.id], {
                'name': form['name'],
                'vat_no':form['vat_no'],
                'cst_no':form['cst_no'],
                'pan_no':form['pan_no'],
                'ser_tax':form['sr_tax'],
                'excise':form['excise'],
                'range':form['range'],
                'div':form['div'],
            })
        values={
                    'name': form['name'],
                    'street': form['street'],
                    'street2': form['street2'],
                    'zip': form['zip'],
                    'city': form['city'],
                    'email': form['email'],
                    'phone': form['phone'],
                    'country_id': form['country_id'],
                }
        if form['state_id'] > 0:
            values['state_id']=form['state_id']
        if company.partner_id.address:
            address=company.partner_id.address[0]
            address_obj.write(cr, uid, [address.id], values)
        else:
            values['partner_id']=company.partner_id.id
            add_id=address_obj.create(cr, uid, values)

        cr.commit()
        (db, pool)=pooler.restart_pool(cr.dbname, update_module=True)

        return {}

    def _menu(self, cr, uid, data, context):
        users_obj=pooler.get_pool(cr.dbname).get('res.users')
        action_obj=pooler.get_pool(cr.dbname).get('ir.actions.act_window')

        ids=action_obj.search(cr, uid, [('name', '=', 'Menu')])
        menu=action_obj.browse(cr, uid, ids)[0]

        ids=users_obj.search(cr, uid, [('action_id', '=', 'Setup')])
        users_obj.write(cr, uid, ids, {'action_id': menu.id})
        ids=users_obj.search(cr, uid, [('menu_id', '=', 'Setup')])
        users_obj.write(cr, uid, ids, {'menu_id': menu.id})

        return {
            'name': menu.name,
            'type': menu.type,
            'view_id': (menu.view_id and\
                    (menu.view_id.id, menu.view_id.name)) or False,
            'domain': menu.domain,
            'res_model': menu.res_model,
            'src_model': menu.src_model,
            'view_type': menu.view_type,
            'view_mode': menu.view_mode,
            'views': menu.views,
        }

    def _next(self, cr, uid, data, context):
        if not data['form']['profile'] or data['form']['profile'] <= 0:
            return 'company'
        return 'charts'

    def _previous(self, cr, uid, data, context):
        if 'profile' not in data['form'] or data['form']['profile'] <= 0:
            return 'init'
        return 'charts'

    def _config(self, cr, uid, data, context=None):
        users_obj=pooler.get_pool(cr.dbname).get('res.users')
        action_obj=pooler.get_pool(cr.dbname).get('ir.actions.act_window')

        ids=action_obj.search(cr, uid, [('name', '=', 'Menu')])
        menu=action_obj.browse(cr, uid, ids)[0]

        ids=users_obj.search(cr, uid, [('action_id', '=', 'Setup')])
        users_obj.write(cr, uid, ids, {'action_id': menu.id})
        ids=users_obj.search(cr, uid, [('menu_id', '=', 'Setup')])
        users_obj.write(cr, uid, ids, {'menu_id': menu.id})
        return {
                'view_type': 'form',
                "view_mode": 'form',
                'res_model': 'ir.actions.configuration.wizard',
                'type': 'ir.actions.act_window',
                'context':{'menu':True},
                'target':'new',
         }
        
    fields={
        'profile':{
            'string':'Profile',
            'type':'selection',
            'selection':_get_profiles,
           # 'default': -1,
            'required': True,
        },
        'name':{
            'string': 'Company Name',
            'type': 'char',
            'size': 64,
        },
        'street':{
            'string': 'Street',
            'type': 'char',
            'size': 128,
        },
        'street2':{
            'string': 'Street2',
            'type': 'char',
            'size': 128,
        },
        'zip':{
            'string': 'Zip code',
            'type': 'char',
            'size': 24,
        },
        'city':{
            'string': 'City',
            'type': 'char',
            'size': 128,
        },
        'state_id':{
            'string': 'State',
            'type': 'selection',
            'selection':_get_states,
        },
        'country_id':{
            'string': 'Country',
            'type': 'selection',
            'selection':_get_countries,
        },
        'email':{
            'string': 'E-mail',
            'type': 'char',
            'size': 64,
        },
        'phone':{
            'string': 'Phone',
            'type': 'char',
            'size': 64,
        },
        'currency': {
            'string': 'Currency',
            'type': 'many2one',
            'relation': 'res.currency',
            'required': True,
        },
        'vat_no': {
            'string': 'VAT Number',
            'type': 'char',
            'size': 64,
        },
        'cst_no': {
            'string': 'CST Number',
            'type': 'char',
            'size': 64,
        },
        'pan_no': {
            'string': 'PAN Number',
            'type': 'char',
            'size': 64,
        },
        'sr_tax': {
            'string': 'Service Tax Number',
            'type': 'char',
            'size': 64,
        },
        'excise': {
            'string': 'Exices Number',
            'type': 'char',
            'size': 64,
        },
        'range': {
            'string': 'Range',
            'type': 'char',
            'size': 64,
        },
        'div': {
            'string': 'Division',
            'type': 'char',
            'size': 64,
        },
        'rml_header1':{
            'string': 'Report Header',
            'type': 'char',
            'help': """This sentence will appear at the top right corner of your reports.
We suggest you to put a slogan here:
"Open Source Business Solutions".""",
            'size': 200,
        },
        'rml_footer1':{
            'string': 'Report Footer 1',
            'type': 'char',
            'help': """This sentence will appear at the bottom of your reports.
We suggest you to write legal sentences here:
Web: http://openerp.com - Fax: +32.81.73.35.01 - Fortis Bank: 126-2013269-07""",
            'size': 200,
        },
        'rml_footer2':{
            'string': 'Report Footer 2',
            'help': """This sentence will appear at the bottom of your reports.
We suggest you to put bank information here:
IBAN: BE74 1262 0121 6907 - SWIFT: CPDF BE71 - VAT: BE0477.472.701""",
            'type': 'char',
            'size': 200,
        },
        'logo':{
            'string': 'Logo',
            'type': 'binary',
        },
    }
    states={
        'init':{
            'actions': [_get_company],
            'result': {'type': 'form', 'arch': view_form_profit, 'fields': fields,
                'state': [
                    ('menu', 'Cancel', 'gtk-cancel'),
                    ('company', 'Next', 'gtk-go-forward', True)
                ]
            }
        },
#        'next': {
#            'actions': [],
#            'result': {'type': 'choice', 'next_state': _next}
#        },
#        'charts':{
#            'actions': [],
#            'result': {'type': 'form', 'arch': view_form_charts, 'fields': fields,
#                'state':[
#                    ('init', 'Previous', 'gtk-go-back'),
#                    ('company', 'Next', 'gtk-go-forward', True)
#                ]
#            }
#        },
        'company':{
            'actions': [],
            'result': {'type': 'form', 'arch': view_form_company, 'fields': fields,
                'state': [
                    ('init', 'Previous', 'gtk-go-back'),
                    ('update', 'Next', 'gtk-go-forward', True)
                ]
            }
        },
#        'previous':{
#            'actions': [],
#            'result': {'type': 'choice', 'next_state': _previous}
#        },
        'update':{
            'actions': [],
            'result': {'type': 'form', 'arch': view_form_update, 'fields': fields,
                'state': [
                    ('company', 'Previous', 'gtk-go-back'),
                    ('finish', 'Install', 'gtk-ok', True)
                ]
            }
        },
        'finish':{
            'actions': [_update],
            'result': {'type': 'form', 'arch': view_form_finish, 'fields': {},
                'state': [
                    ('menu', 'Use Directly', 'gtk-ok'),
                    ('config', 'Start Configuration', 'gtk-go-forward', True)
                ]
            }
        },
        'config': {
            'result': {
                'type': 'action',
                'action': _config,
                'state': 'end',
            },
        },
        'menu': {
            'actions': [],
            'result': {'type': 'action', 'action': _menu, 'state': 'end'}
        },
    }
    
voucher_wizard_base_setup('base_setup.voucher_base_setup1')
