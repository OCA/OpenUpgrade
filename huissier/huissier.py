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

import time

import netsvc
from osv import fields, osv, orm
import ir

acquis_strings = {
    'fr': u'Pour acquit',
    'nl': u'Voor ontvangst'
}

#----------------------------------------------------------
# Dossier
#----------------------------------------------------------
class huissier_dossier(osv.osv):
    _name = "huissier.dossier"
    _auto = True
    _order = 'num_vignette desc'
    _rec_name = 'num_vignette'

    def _adjudication_get(self, cr, uid, ids, field_name=None, arg=None, context={}):
        res = {}
        for id in ids:
            res[id]=0.0
            cr.execute("select sum(adj_price) from huissier_lots where dossier_id=%s", (id,))
            sum = cr.fetchone()
            res[id] = sum and sum[0] or 0.0
        return res

    def _costs_get(self, cr, uid, ids, field_name=None, arg=None, context={}):
        dossiers = self.browse(cr, uid, ids)
        res = {}
        for d in dossiers:
            costs = [l.amount_costs for l in d.lot_id]
            cost_amount = reduce(lambda x, y: x+y, costs, 0.0)
            res[d.id] = cost_amount
        return res

    def _total_get(self, cr, uid, ids, field_name=None, arg=None, context={}):
        res = {}
        for id in ids:
            adj = self._adjudication_get(cr, uid, [id])[id]
            costs = self._costs_get(cr, uid, [id])[id]
            res[id] = adj + costs
        return res

    def _room_costs_get(self, cr, uid, ids, prop=None, unknown_none=None, unknown_dict={}):
        res={}
        lots=self.browse(cr,uid,ids)
        pt_tax=self.pool.get('account.tax')
        for lot in lots:
            amount_total=0.0
            total = self._adjudication_get(cr, uid, [lot.id])[lot.id]
            taxes=[]
            amount_total=0.0
            if lot.room_cost_id:
                taxes.append(lot.room_cost_id)
            costs =pt_tax.compute(cr, uid, taxes, total, 1)
            for t in taxes:
                amount_total+=t['amount']
            res[lot.id]=amount_total
        return res

    _columns = {
#       'name': fields.integer(u'Numéro de vignette'),
        'num_vignette': fields.integer(u'Numéro de vignette', required=True),
        #domain="[('category_id','=','Etudes')]",
        'etude_id': fields.many2one('res.partner', u'Etude', required=True),
        'date_creation': fields.date(u'Création'),
        'creancier': fields.many2one('res.partner', u'Créancier'),
#       'creancier_name': fields.char('Nom', size=64),
#       'creancier_address': fields.char('Adresse', size=128),
#       'creancier_zip': fields.char('Code postal', change_default=True, size=24),
#       'creancier_city': fields.char('Ville', size=64),
        'debiteur': fields.many2one('res.partner', u'Débiteur'),
#       'debiteur_name': fields.char('Nom', size=64),
#       'debiteur_address': fields.char('Adresse', size=128),
#       'debiteur_zip': fields.char('Code postal', change_default=True, size=24),
#       'debiteur_city': fields.char('Ville', size=64),
#       'debiteur_naissance': fields.date('Date de naissance'),
#       'debiteur_tva':fields.char('TVA', size=32),
        'date_prevue': fields.date(u'Date prévue'),
        'date_reelle': fields.date(u'Date réelle'),
        'lang': fields.selection((('fr',u'Français'),('nl',u'Néerlandais')), u'Langue', required=True),
        'toinvoice': fields.boolean(u'Facturer?'),
        'tolist': fields.boolean(u'Listing palais?'),
        'cost_id': fields.many2one('account.tax', u'Frais de Vente', domain="[('domain','=','frais')]"),
        'room_cost_id': fields.many2one('account.tax', u'Frais de Salle', domain="[('domain','=','salle')]"),
        'amount_adj': fields.float(u'Adjudications', digits=(14,2)),
        'amount_adj_calculated': fields.function(_adjudication_get, store=True, method=True, string=u'Adjudications'),
        'amount_costs': fields.function(_costs_get, method=True, string=u'Frais',store=True),
        'amount_total': fields.function(_total_get, method=True, string=u'Total',store=True),
        'amount_room_costs': fields.function(_room_costs_get,method=True,string=u'Frais de salle' ,store=True ),
        'amount_voirie': fields.float(u'Frais de voirie', digits=(12,2)),
        'state': fields.selection((('draft',u'Ouvert'),('closed',u'Fermé'),('canceled',u'Annulé')), u'État', readonly=True),
        'lot_id': fields.one2many('huissier.lots', 'dossier_id', u'Objets'),
        'invoice_id': fields.many2one('account.invoice', u'Facture'),
        'refund_id': fields.many2one('account.invoice', u'Facture remboursée'),
        'salle_account_id': fields.many2one('account.account', 'Compte Frais de Salle'),
        'voirie_account_id': fields.many2one('account.account', 'Compte Frais de Voirie'),
#       'expense_account_id': fields.many2one('account.account', 'Expense Account', required=True),
        'deposit_id': fields.one2many('huissier.deposit', 'dossier_id', u'Garde meuble'),
    }
    _defaults = {
        'toinvoice': lambda *a: True,
        'tolist': lambda *a: True,
        'state': lambda *a: 'draft',
        'date_creation': lambda *a: time.strftime('%Y-%m-%d'),
        'date_prevue': lambda *a: time.strftime('%Y-%m-%d'),
        'date_reelle': lambda *a: time.strftime('%Y-%m-%d'),
    }

    # check
    def _constraint_num_exists(self, cr, uid, ids):
        dossiers = self.read(cr, uid, ids, ['num_vignette'])
        dossier = dossiers and dossiers[0] or False
        num = dossier and dossier['num_vignette'] or 0

        res = self.pool.get('huissier.vignettes').search(cr, uid, [('first', '<=', num), ('last', '>=', num)])
        return bool(res)

    def _constraint_num_unique(self, cr, uid, ids):
        dossiers = self.read(cr, uid, ids, ['num_vignette'])
        dossier = dossiers and dossiers[0] or False
        num = dossier and dossier['num_vignette'] or 0

        prev_dossiers = self.search(cr, uid, [('num_vignette','=',num)]) #, ('state','<>','canceled')])
        return len(prev_dossiers)==1

    _constraints = [
        (_constraint_num_exists, "Ce numero de vignette n'existe pas!", []), # ['num_vignette']) # .encode('utf8')
        (_constraint_num_unique, 'Ce numero de vignette a deja ete utilise pour un autre dossier!', []) # ['num_vignette']) # .encode('utf8')
    ]

    def name_get(self, cr, uid, ids, context={}):
        if not len(ids):
            return []

        res = []
        for r in self.browse(cr, uid, ids):
            name = r.num_vignette and u'%d: ' % r.num_vignette or u''
            name += r.etude_id.name
            name += r.debiteur and u' (%s)' % r.debiteur.name or u''
            res.append((r['id'], name))
        return res

    def name_search(self, cr, user, name='', args=[], operator='ilike', context={}):
        try:
            num_vignette = int(name)
            ids = self.search(cr, user, [('num_vignette','=',num_vignette)] + args)
        except:
            if name:
                ids = self.search(cr, user, [('etude_id','ilike',name)] + args)
            else:
                ids = self.search(cr, user, args)
        return self.name_get(cr, user, ids, context)

    def onchange_num_vignette(self, cr, uid, ids, num):
        cr.execute("select id,name from res_partner where id=(select etude_id from huissier_vignettes where %s >= first and %s <= last)", (num,num))
        res = cr.dictfetchall()
        return res and {'value': {'etude_id': (res[0]['id'],res[0]['name'])}} or {}

    def invoice(self, cr, uid, ids, acquis=False):
        """
            Create an invoice for one dossier
        """
        assert len(ids)==1

        dt = time.strftime('%Y-%m-%d')

        frais_salle_str = {
            'fr': u'Frais de salle',
            'nl': u'Zaalkosten',
        }

        frais_voirie_str = {
            'fr': u'Frais de voirie',
            'nl': u'Vuilniskosten',
        }

        invoice_desc_str = {
            'fr': u'Facture de frais de salle',
            'nl': u'Faktuur zaalkosten',
        }

        invoice_ids = []
        for dossier in self.browse(cr, uid, ids):
            etude = dossier.etude_id
            lang = etude.lang or 'fr'
        #   account_receive_id = ir.ir_get(cr,uid,[('meta','res.partner'), ('name','account.receivable')], [('id',str(etude.id))] )[0][2]
            account_receive_id=dossier.etude_id.property_account_receivable.id
            lines = []
            invoice_desc = invoice_desc_str[lang]
            line_desc = frais_salle_str[lang]
            if dossier.num_vignette:
                invoice_desc += ' (%d)' % dossier.num_vignette
                line_desc += ' (%d)' % dossier.num_vignette
            if dossier.debiteur:
                line_desc += u' %s' % dossier.debiteur.name

#CHECKME: fo des taxes pour les factures de salle?
            lines.append((0,False, {'name':line_desc, 'quantity':1, 'account_id':dossier.salle_account_id.id, 'price_unit':dossier.amount_room_costs}))

            if dossier.amount_voirie:
                line_desc = frais_voirie_str[lang]
                lines.append((0,False, {'name':line_desc, 'quantity':1, 'account_id':dossier.voirie_account_id.id, 'price_unit':dossier.amount_voirie}))

            addr = self.pool.get('res.partner').address_get(cr, uid, [etude.id], ['contact','invoice'])
            number = self.pool.get('ir.sequence').get(cr, uid, 'huissier.invoice.salle')

            new_invoice = {
                'name': invoice_desc,
                'number': number,
                'state': 'draft',
                'partner_id': etude.id,
                'address_contact_id': addr['contact'],
                'address_invoice_id': addr['invoice'],
                'origin': etude.ref,
                'date_invoice': dt,
                'date_due': dt,
                'invoice_line': lines,
                'type': 'out_invoice',
                'account_id': account_receive_id,
                'comment': acquis and acquis_strings.get(lang, 'Pour acquit') or False,
                'fiscal_position': etude.property_account_position and etude.property_account_position.id or False
            }
            invoice_id = self.pool.get('account.invoice').create(cr, uid, new_invoice)
            self.write(cr, uid, ids, {'invoice_id':invoice_id})
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'account.invoice', invoice_id, 'invoice_open', cr)
            invoice_ids.append(invoice_id)
        return invoice_ids

#   def create_invoice_and_cancel_old(self, cr, uid, ids):
    def create_invoice_and_refund_old(self, cr, uid, ids, acquis=False):
        assert len(ids)==1
        dossier = self.read(cr, uid, ids, ['invoice_id']) #[0]['invoice_id'][0]
        invoice = dossier[0]['invoice_id']
        invoice_id = invoice and invoice[0] or False

#faudrait sans doute faire un wizard dans lequel il demande si annulation ou note de credit
        refund_id = False

        if invoice_id:
            # cancel old invoice
#           wf_service = netsvc.LocalService("workflow")
#           wf_service.trg_validate(uid, 'account.invoice', invoice_id, 'invoice_cancel', cr)a

            # refund old invoice
            refund_id = self.pool.get('account.invoice').refund(cr, uid, [invoice_id])[0]
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'account.invoice', refund_id, 'invoice_open', cr)
        # create a new invoice
        invoice_id = self.invoice(cr, uid, ids, acquis)[0]
        return (refund_id, invoice_id)

    def close(self, cr, uid, ids, frais_voirie=False, acquis=False):
        assert len(ids)==1
        if isinstance(frais_voirie, float):
            self.write(cr, uid, ids, {'amount_voirie': frais_voirie})
        toinvoice = self.read(cr, uid, ids, ['toinvoice'])[0]['toinvoice']
        if toinvoice:
#           self.create_invoice_and_cancel_old(cr, uid, ids)
            (refund_id, invoice_id) = self.create_invoice_and_refund_old(cr, uid, ids, acquis)
        else:
            (refund_id, invoice_id) = (False, False)
        # stores amount adjudicated for faster retrieval later
        amount_adj = self.read(cr, uid, ids, ['amount_adj_calculated'])[0]['amount_adj_calculated']
        self.write(cr, uid, ids, {'state':'closed', 'amount_adj':amount_adj,'refund_id':refund_id})
        return (refund_id, invoice_id)

    def cancel(self, cr, uid, ids,context):
        self.write(cr, uid, ids, {'state':'canceled'})
        return True

huissier_dossier()

def _lang_get(self, cr, user,ids):
    cr.execute('select code, name from res_lang order by name')
    return cr.fetchall() or [(False, '/')]

#----------------------------------------------------------
# Lots
#----------------------------------------------------------
class huissier_lots(osv.osv):
    _name = "huissier.lots"
    _auto = True
    _order = "number"
    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=80):
        if not args:
            args=[]
        if not context:
            context={}
        ids = []
        if name and name.startswith('ID'):
            try:
                ids = self.search(cr, uid, [('id', '=', int(name[2:]))] + args, limit=limit, context=context)
            except:
                ids=[]
        if not ids:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context)

    def _get_price_wh_costs(self, cr, uid, ids, name, arg, context):
        res = {}
        for obj in self.browse(cr, uid, ids):
            try:
                res[obj.id] = obj.adj_price + obj.adj_price * obj.dossier_id.cost_id.amount
            except:
                res[obj.id] = 0.0
        return res

    def _get_costs(self, cr, uid, ids, name, arg, context):
        res = {}
        cr.execute("select id, dossier_id, adj_price from huissier_lots where id in ("+','.join([str(id) for id in ids])+")")
        for (id, dossier, price) in cr.fetchall():
#FIXME: there is a bug somewhere: the 0.0 from a spinint gets saved as a None value in the DB :(
            if not price:
                price = 0.0
            res[id] = self.get_costs_amount(cr, uid, ids, dossier, price)
        return res
    def button_not_bought(self,cr,uid,ids,*a):
        return self.write(cr,uid,ids, {'state':'non_vendu'})

    def button_draft(self,cr,uid,ids,*a):
        return self.write(cr,uid,ids, {'state':'draft'})

    def button_emporte(self,cr,uid,ids,*a):
        return self.write(cr,uid,ids, {'state':'emporte'})

    def button_bought(self,cr,uid,ids,*a):
        return self.write(cr,uid,ids, {'state':'vendu'})

    _columns = {
        'dossier_id': fields.many2one('huissier.dossier', u'Dossier huissier'),
        'number': fields.integer(u'Lot', required=True, readonly=True),
        'name': fields.char(u'Description', size=256, required=True),
        'vat': fields.many2one('account.tax', u'Taxe', domain="[('domain','=','tva')]", required=True),
        'adj_price': fields.float(u"Prix d'adjudication", digits=(12,2)),
        'buyer_ref': fields.many2one('res.partner', 'Client'),
#       'buyer_ref': fields.char(u'Réf. client', size=64),
#       'buyer_name': fields.char(u'Nom et Prénom', size=64),
 #      'buyer_firstname': fields.char(u'Prénom', size=64),
    #"""enleve et remplace par champ partner.address
        'buyer_name': fields.char(u'Nom', size=64),
        'buyer_address': fields.char(u'Adresse', size=128),
        'buyer_zip': fields.char(u'Code postal', change_default=True, size=24),
        'buyer_city': fields.char(u'Ville', size=64),
        'image': fields.binary('Image'),
#       'buyer_address': fields.many2one('res.partner.address', 'Adresse Acheteur'),
        'buyer_birthdate': fields.char(u'Date de naissance', size=64),
        'buyer_vat': fields.char(u'TVA', size=64),
        'buyer_lang': fields.selection(_lang_get, 'Langue', size=2),
        'amount_costs': fields.function(_get_costs, method=True, string=u'Frais',store=True),
#       'amount_costs': fields.function(_get_costs, method=True, string=u'Frais', digits=(12,2)),
        'price_wh_costs': fields.function(_get_price_wh_costs, method=True, string=u'A payer'),
#       'payer':fields.boolean('payer'),
#       'price_wh_costs': fields.function(_get_price_wh_costs, method=True, string=u'A payer', digits=(12,2)),
        'state': fields.selection((('draft','Brouillon'),('non_vendu','Non vendu'),('vendu','vendu'),('emporte',u'Emporté')),'State',  readonly=True),
    }
    _defaults = {
        'number': lambda obj,cr,uid,*a: obj._get_next_lot_number(cr, uid),
        'vat': lambda obj,cr,uid,*a: obj._get_lot_default_vat(cr, uid),
        'state': lambda *a: 'draft',
#       'payer': lambda *a: 'True',
    }


    # returns the highest lot number used in dossiers created this year
    def _get_yearly_max_lot_number(self, cr, uid):
        year = time.strftime('%Y')
        # Ceci aura un comportement "inattendu" si le dossier est créé fin
        # d'année, réellement vendu au début de l'année suivante et
        # que la date réelle du dossier n'a pas été mise à jour.
        # Peut être qu'a chaque nouveau lot pour ce dossier, je devrais
        # mettre a jour la date réelle?
        cr.execute(
            "select max(number) as number " \
            "from huissier_lots as l left join huissier_dossier as d on l.dossier_id=d.id " \
            "where coalesce(date_reelle, date_creation) >= '%s-01-01'" % (year,)
        )
        res = cr.dictfetchall()
        return res[0]['number'] or 0

    def _get_next_lot_number(self, cr, uid):
#       return int(self.pool.get('ir.sequence').get(cr, uid, 'huissier.lots'))
        return self._get_yearly_max_lot_number(cr, uid)+1

    # returns the vat used in the lot with the highest number in dossiers created this year
    def _get_lot_default_vat(self, cr, uid):
        lot_number = self._get_yearly_max_lot_number(cr, uid)
        year = time.strftime('%Y')
        cr.execute(
            "select vat " \
            "from huissier_lots as l left join huissier_dossier as d on l.dossier_id=d.id " \
            "where number = %d " \
            "and coalesce(date_reelle, date_creation) >= '%s-01-01'" % (lot_number, year)
        )
        res = cr.dictfetchall()
        return res and res[0]['vat'] or False

    def get_costs_amount(self, cr, uid, ids, dossier_id, adj_price):
        res={}
#       dossier = self.pool.get('huissier.dossier').read(cr, uid, [dossier_id], ['cost_id'])[0]

        pt_tax=self.pool.get('account.tax')
        taxes=[]
        amount_total=0.0
        obj_lot=self.browse(cr,uid,ids)[0]
        if obj_lot.dossier_id:
            taxes.append(obj_lot.dossier_id.cost_id)
        costs = pt_tax.compute(cr, uid, taxes, obj_lot.adj_price, 1)
        for t in taxes:
            amount_total+=t['amount']
        #res[obj_lot.id]=amount_total
#       cost_amount = reduce(lambda x, y: x+y['amount'], costs, 0.0)
        return amount_total

    def onchange_adj_price(self, cr, uid, ids, dossier_id, adj_price):
        return {'value':{'price_wh_costs': adj_price + self.get_costs_amount(cr, uid, ids, dossier_id, adj_price)}}

    def onchange_buyer_ref(self, cr, uid, ids, buyer_id):
#       cr.execute('select id from res_partner where ref=%s', (buyer_ref,)) # and category = client
#       res = cr.dictfetchall()
#       if not len(res):
        if not buyer_id:
            return {
                'value': {'buyer_name':False, 'buyer_address':False, 'buyer_zip':False, 'buyer_city':False, 'buyer_birthdate':False, 'buyer_vat':False, 'buyer_lang':False},
                'readonly': {'buyer_name':False, 'buyer_address':False, 'buyer_zip':False, 'buyer_city':False, 'buyer_birthdate':False, 'buyer_vat':False, 'buyer_lang':False}
            }
                #return {'value': {'buyer_name':False, 'buyer_address':False, 'buyer_zip':False, 'buyer_city':False, 'buyer_birthdate':False, 'buyer_vat':False, 'buyer_lang':False},
                #'readonly': {'buyer_name':False, 'buyer_address':False, 'buyer_zip':False, 'buyer_city':False, 'buyer_birthdate':False, 'buyer_vat':False, 'buyer_lang':False}
        partner = self.pool.get('res.partner').browse(cr, uid, buyer_id)
        address = partner.address[0]
        return {
            'value': {'buyer_name':partner.name, 'buyer_address':address.street, 'buyer_zip':address.zip, 'buyer_city':address.city, 'buyer_birthdate':address.birthdate, 'buyer_vat':partner.vat, 'buyer_lang':partner.lang},
            'readonly': {'buyer_name':True, 'buyer_address':True, 'buyer_zip':True, 'buyer_city':True, 'buyer_birthdate':True, 'buyer_vat':True, 'buyer_lang':True}
        }


huissier_lots()

class huissier_vignettes(osv.osv):
    _name = "huissier.vignettes"
    _auto = True
    _order = "first"

    def _get_range_value(self, cr, uid, ids, name, arg, context):
        res = {}
        cr.execute("select id, price, quantity from huissier_vignettes where id in ("+','.join([str(id) for id in ids])+")")
        for (id, price, quantity) in cr.fetchall():
#FIXME: there is a bug somewhere: the 0.0 from a spinint gets saved as a None value in the DB :(
#           if not price:
#               price = 0.0
            res[id] = price * quantity
        return res

    #   'etude_id': fields.many2one('res.partner', u'Etude', domain="[('category_id', '=', 'Etudes')]", required=True, states={'invoiced':[('readonly',True)],'paid':[('readonly',True)]}),
    _columns = {
        'etude_id': fields.many2one('res.partner', u'Etude', domain="[('category_id', '=', 'Etudes')]", states={'invoiced':[('readonly',True)],'paid':[('readonly',True)]}),
        'price': fields.float(u'Prix unitaire', digits=(12,2), required=True, states={'invoiced':[('readonly',True)],'paid':[('readonly',True)]}),
        'quantity': fields.integer(u'Quantité', required=True, states={'invoiced':[('readonly',True)],'paid':[('readonly',True)]}),
        'first': fields.integer(u'Référence de départ', required=True, states={'invoiced':[('readonly',True)],'paid':[('readonly',True)]}),
        'last': fields.integer(u'Référence de fin', required=True, states={'invoiced':[('readonly',True)],'paid':[('readonly',True)]}),
        'acquis': fields.boolean(u'Pour acquis', states={'invoiced':[('readonly',True)],'paid':[('readonly',True)]}),
        'invoice_id': fields.many2one('account.invoice', u'Facture', readonly=True),
    # n existe plus 'transfer_id': fields.many2one('account.transfer', u'Payement', readonly=True),
        'income_account_id': fields.many2one('account.account', 'Compte Revenus', required=True, states={'invoiced':[('readonly',True)],'paid':[('readonly',True)]}),
        'date_creation': fields.datetime(u'Date de création'),
#       'state': fields.selection( (('draft',u'draft'),('waiting',u'en attente'),('invoiced',u'facturées')),u'État', readonly=True),
        'state': fields.selection( (('draft',u'draft'),('invoiced',u'facturées'),('paid',u'payées')),u'État', readonly=True),
        'value': fields.function(_get_range_value, method=True, string=u'A payer'),
        #   'refund_id': fields.many2one('account.invoice', u'Facture remboursee', readonly=True),


    }
    _defaults = {
        'date_creation': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'price': lambda *a: 11.0,
        'first': lambda obj,cr,uid,*a: obj._get_next_first_number(cr, uid),
        'state': lambda *a: 'draft',

    }

    def _get_next_first_number(self, cr, uid):
        cr.execute('select max(last)+1 as number from huissier_vignettes where first<900000')
        res = cr.dictfetchall()
        return res[0]['number'] or 1
#       return int(self.pool.get('ir.sequence').get(cr, uid, 'huissier.vignettes'))

    def onchange_quantity(self, cr, uid, ids, quantity, first):
        return {'value':{'last':first + quantity - 1}}

    def onchange_last(self, cr, uid, ids, first, last):
        if last < first:
            return {}
        else:
            return {'value':{'quantity':last - first + 1}}
    #remplace sur l objet pay des factures
#   def pay(self, cr, uid, ids, account_id):
#       label_ranges = self.browse(cr, uid, ids)
#       if not len(label_ranges):
#           return []
#
#       for lr in label_ranges:
#           partner_id = lr.etude_id.id
#           account_src_id = ir.ir_get(cr,uid,[('meta','res.partner'), ('name','account.receivable')], (partner_id or []) and [('id',str(partner_id))] )[0][2]
#           transfer_name = u'Payement des vignettes %d à %d (%d vignettes)' % (lr.first, lr.last, lr.quantity)
#           transfer = {
#               'name': transfer_name,
#               'partner_id': partner_id,
#               'account_src_id': account_src_id,
#               'type': 'in_payment',
#               'account_dest_id': account_id,
#               'amount': lr.value,
#           }
#       #   transfer_id = self.pool.get('account.transfer').create(cr, uid, transfer)
#       #   self.pool.get('account.transfer').pay_validate(cr,uid,[transfer_id])
#
#       #   self.write(cr, uid, [lr.id], {'transfer_id':transfer_id, 'state':'paid'})
#
    def invoice(self, cr, uid, ids,context):
        """
            Create an invoice for selected range of 'vignettes' (ids)
        """
        dt = time.strftime('%Y-%m-%d')

        label_ranges = self.browse(cr, uid, ids)
        if not len(label_ranges):
            return []

#TODO; raise except if quantity == 0

        # group label ranges by etude
        # ie create a dictionary containing lists of label ranges
        label_ranges_etude = {}
        for lr in label_ranges:
            if not lr.etude_id in label_ranges_etude:
                label_ranges_etude[lr.etude_id] = []
            label_ranges_etude[lr.etude_id].append(lr)

        line_descs = {
            'fr': u'vignette(s) (%d --> %d)',
            'nl': u'vignette(n) (%d --> %d)'
        }

        invoice_descs = {
            'fr': u'Facture de vignettes (%d vignette(s))',
            'nl': u'Vignetten faktuur (%d vignette(n))'
        }
        # use each list of label ranges in turn
        for label_ranges in label_ranges_etude.values():
            etude = label_ranges[0].etude_id
            lang = etude.lang or 'fr'
            label_quantity = reduce(lambda total, lr: total + lr['quantity'], label_ranges, 0.0)
            invoice_desc = invoice_descs[lang] % (label_quantity,)
            account_receive_id=label_ranges[0].etude_id.property_account_receivable.id
            lines = []
            for lr in label_ranges:
                line_desc = line_descs[lang] % (lr.first, lr.last)
                lines.append((0,False, {'name':line_desc, 'quantity':lr.quantity, 'account_id':lr.income_account_id.id, 'price_unit':lr.price}))

            addr = self.pool.get('res.partner').address_get(cr, uid, [etude.id], ['contact','invoice'])

            # get the number from the sequence (we set it manually)
            number = self.pool.get('ir.sequence').get(cr, uid, 'huissier.invoice.vignettes')
            new_invoice = {
                'number': number,
                'name': invoice_desc,
                'state': 'draft',
                'partner_id': etude.id,
                'address_contact_id': addr['contact'],
                'address_invoice_id': addr['invoice'],
            #   'partner_ref': etude.ref,
                'date_invoice': dt,
                'date_due': dt,
                'invoice_line': lines,
                'type': 'out_invoice',
                'account_id': account_receive_id,
                'comment': lr.acquis and acquis_strings[lang] or False,
                'fiscal_position': etude.property_account_position and etude.property_account_position.id or False
            }

            invoice_id = self.pool.get('account.invoice').create(cr, uid, new_invoice)

            lr_ids = [lr.id for lr in label_ranges]
            self.write(cr, uid, lr_ids, {'invoice_id':invoice_id, 'state':'invoiced'})
huissier_vignettes()

#----------------------------------------------------------
# Deposit
#----------------------------------------------------------
class huissier_deposit(osv.osv):
    _name = "huissier.deposit"
    _auto = True
    _order = "rentree_mobilier"
    _columns = {
        'dossier_id': fields.many2one('huissier.dossier', u'Dossier', states={'running':[('readonly',True)],'closed':[('readonly',True)]}),
        'line_desc': fields.char(u'Libellé', size=256, required=True, states={'running':[('readonly',True)],'closed':[('readonly',True)]}),
        'billing_partner_id': fields.many2one('res.partner', u'Partenaire à facturer', required=True, states={'running':[('readonly',True)],'closed':[('readonly',True)]}),
        'rentree_mobilier': fields.date(u'Mobilier rentré le', required=True, states={'running':[('readonly',True)],'closed':[('readonly',True)]}),
        'sortie_mobilier': fields.date(u'Retiré le', states={'running':[('readonly',True)],'closed':[('readonly',True)]}),
        'cubage': fields.float(u'Cubage (m³)', digits=(12,2), states={'running':[('readonly',True)],'closed':[('readonly',True)]}),
        'prix_garde_meuble': fields.float(u'Prix au m³/mois', digits=(12,2), required=True, states={'running':[('readonly',True)],'closed':[('readonly',True)]}),
        'nombre_vehicule': fields.integer(u'Nombre de véhicules', states={'running':[('readonly',True)],'closed':[('readonly',True)]}),
        'forfait_vehicule': fields.float(u'Forfait véhicule', digits=(12,2), required=True, states={'running':[('readonly',True)],'closed':[('readonly',True)]}),
        'nombre_expo': fields.integer(u"Nombre d'expositions", states={'running':[('readonly',True)],'closed':[('readonly',True)]}),
        'forfait_expo': fields.float(u'Forfait exposition', required=True, digits=(12,2), states={'running':[('readonly',True)],'closed':[('readonly',True)]}),
        'acquis': fields.boolean(u'Pour acquis', states={'running':[('readonly',True)],'closed':[('readonly',True)]}),
        'income_account_id': fields.many2one('account.account', u'Compte Revenus', required=True, states={'running':[('readonly',True)],'closed':[('readonly',True)]}),
        'invoice_id': fields.many2many('account.invoice', 'huissier_deposit_invoice_rel', 'deposit_id', 'invoice_id', u'Factures', readonly=True),
        'state': fields.selection((('draft',u'draft'),('running',u'en cours'),('closed',u'retiré')), u'Statut', readonly=True),
    }
    _defaults = {
        'state': lambda *a: 'draft',
    }

    def invoice(self, cr, uid, ids):
        dt = time.strftime('%Y-%m-%d')

        line_descs_vehicule = {
            'fr': u'Forfait pour véhicule',
            'nl': u'Voertuig Forfait'
        }

        line_descs_expo = {
            'fr': u"Frais d'exposition",
            'nl': u'Expositie kosten'
        }

        invoice_descs = {
            'fr': u'Facture de garde meuble',
            'nl': u'Faktuur meubelbewaring'
        }


        invoice_ids = []
        for deposit in self.browse(cr, uid, ids):
            partner = deposit.billing_partner_id

            dossier_id = deposit.dossier_id.id
            lang = partner.lang or 'fr'

            invoice_desc = invoice_descs.get(lang, invoice_descs['fr'])

            #account_receive_id = ir.ir_get(cr, uid, [('meta','res.partner'),('name','account.receivable')], [('id',str(partner.id))] )[0][2]

            lines = []
            line_desc = deposit.line_desc
            lines.append((0, False, {'name':deposit.line_desc, 'quantity':deposit.cubage, 'account_id':deposit.income_account_id.id, 'price_unit':deposit.prix_garde_meuble}))

            if deposit.nombre_vehicule:
                line_desc = line_descs_vehicule[lang]
                lines.append((0, False, {'name':line_desc, 'quantity':deposit.nombre_vehicule, 'account_id':deposit.income_account_id.id, 'price_unit':deposit.forfait_vehicule}))

            if deposit.nombre_expo:
                line_desc = line_descs_expo[lang]
                lines.append((0, False, {'name':line_desc, 'quantity':deposit.nombre_expo, 'account_id':deposit.income_account_id.id, 'price_unit':deposit.forfait_expo}))

            addr = self.pool.get('res.partner').address_get(cr, uid, [partner.id], ['contact','invoice'])

            # get the number from the sequence (we set it manually)
            number = self.pool.get('ir.sequence').get(cr, uid, 'huissier.invoice.garde')
            new_invoice = {
                'number': number,
                'name': invoice_desc,
                'state': 'draft',
                'partner_id': partner.id,
                'address_contact_id': addr['contact'],
                'address_invoice_id': addr['invoice'],
                'date_invoice': dt,
                'date_due': dt,
                'invoice_line': lines,
                'type': 'out_invoice',
                'account_id': deposit.billing_partner_id.property_account_receivable.id,
                'comment': deposit.acquis and acquis_strings[lang] or False,
                'fiscal_position': partner.property_account_position and partner.property_account_position.id or False
            }
            invoice_id = self.pool.get('account.invoice').create(cr, uid, new_invoice)
#           'invoice_id': fields.many2many('account.invoice', 'huissier_deposit_invoice_rel', 'deposit_id', 'invoice_id', u'Factures'),
            cr.execute('insert into huissier_deposit_invoice_rel (deposit_id, invoice_id) values (%s, %s)', (deposit.id, invoice_id))
#           self.write(cr, uid, ids, {'invoice_id':invoice_id})
            invoice_ids.append(invoice_id)
        return invoice_ids

    def start_periodic_invoice(self, cr, uid, ids,context):
        self.write(cr, uid, ids, {'state':'running'})
        return True

    def stop_periodic_invoice(self, cr, uid, ids,context):
        self.write(cr, uid, ids, {'state':'closed'})
        return True

    def invoice_once(self, cr, uid, ids,context):
        assert len(ids)==1
        invoice_id = self.invoice(cr, uid, ids)[0]
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(uid, 'account.invoice', invoice_id, 'invoice_open', cr)
        self.write(cr, uid, ids, {'state':'closed'})
        return invoice_id

    def reopen(self, cr, uid, ids,context):
        self.write(cr, uid, ids, {'state':'draft'})
        return True

    def invoice_running_deposits(self, cr, uid, *args):
        ids = self.search(cr, uid, [('state','=','running')])
        self.invoice(cr, uid, ids)

    def onchange_dossier(self, cr, uid, ids, dossier_id):
        dossier = self.pool.get('huissier.dossier').read(cr, uid, [dossier_id], ['etude_id'])[0]
        return {'value':{'billing_partner_id':dossier['etude_id']}}
huissier_deposit()

from mx import DateTime

class huissier_partenaire(osv.osv):
    _inherit = 'res.partner'
    _columns = {
        'image': fields.binary('Image'),
        'date_creation': fields.date(u'Création badge'),
        'date_expiration':fields.date('Expiration badge')
    }
    _defaults = {
        'date_creation': lambda *args: time.strftime('%Y-%m-%d'),
        'date_expiration': lambda *args: (DateTime.now() + DateTime.RelativeDateTime(years=+1)).strftime('%Y-%m-%d'),
        'ref': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'res.partner'),
    }
huissier_partenaire()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

