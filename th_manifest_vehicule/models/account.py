from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError

class ResPartner(models.Model):

    _inherit = 'res.partner'
    balance = fields.Float(string="Balance du compte")
    account_number = fields.Char(string="Numéro de compte")
    operation_ids = fields.One2many('manifest.operation', 'partner_id')
    manifest_ids = fields.One2many('manifest.manifest', 'partner_id')
    solde_compte = fields.Float(string="Solde du compte", compute="_calcul_solde_initail")
    manifest_total = fields.Float(string="Manifest", compute="_calcul_manifest_total")

    def _calcul_manifest_total(self):
        for rec in self:
            total =0
            manifests = self.env['manifest.manifest'].search([('partner_id','=', rec.id)])
            for m in manifests:
                total += 1
            rec.manifest_total = total

    def _calcul_solde_initail(self):
        for rec in self:
            solde =0
            operations = self.env['manifest.operation'].search([('partner_id','=', rec.id),('state','=','confirmed')])
            for op in operations:
                if op.type_operation == '0':
                    solde += op.montant
                else:
                    solde -= op.montant
            rec.solde_compte = solde
    def liste_des_operations(self):
        return{
            'name': ('Opérations'),
            'domain': [('partner_id', '=', self.id)],
            'res_model': 'manifest.operation',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }
    def liste_des_manifest(self):
        return{
            'name': ('Manifests'),
            'domain': [('partner_id', '=', self.id)],
            'res_model': 'manifest.manifest',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }


    

class ManifestOperation(models.Model):

    _name = 'manifest.operation'
    _description = 'Opération'
    _inherit = ['mail.thread','mail.activity.mixin']
    _rec_name="partner_id"

    date = fields.Date("Date d'opération", default=fields.date.today())
    type_operation = fields.Selection([('0', 'Dépôt'),('1','Retrait')])
    montant = fields.Float(string="Montant")
    solde = fields.Float(string="Solde du compte",readonly=True)
    state = fields.Selection([('draft', 'Brouillon'),('confirmed','Confirmer'),('canceled','Annulé')], default='draft', readonly=True,)
    responsable_id = fields.Many2one(
	    'res.users',
	    string='Responsable',
	    default=lambda self: self.env.user.id,
	    readonly=True,
	)

    partner_id = fields.Many2one(
        'res.partner',
        string='Importateur',
        )
    def confirmer_operation(self):
        for rec in self:
            rec.state = 'confirmed'
    def annuller_operation(self):
        for rec in self:
            rec.state = 'canceled'
    def mettre_en_brouillon(self):
        for rec in self:
            rec.state = 'draft'
    @api.onchange('partner_id')
    def _calcul_solde_initail(self):
        for rec in self:
            solde =0
            operations = self.env['manifest.operation'].search([('partner_id','=', rec.partner_id.id),('state','=','confirmed')])
            for op in operations:
                if op.type_operation == '0':
                    solde += op.montant
                else:
                    solde -= op.montant
            rec.solde = solde - rec.montant

    @api.onchange('partner_id','type_operation','montant')
    def _calcul_solde(self):
        for rec in self:
            solde =0
            operations = self.env['manifest.operation'].search([('partner_id','=', rec.partner_id.id),('state','=','confirmed')])
            for op in operations:
                if op.type_operation == '0':
                    solde += op.montant
                else:
                    solde -= op.montant
            if rec.type_operation == '0':
                rec.solde = solde + rec.montant
            else:
                rec.solde = solde - rec.montant

class AccountPayment(models.Model):

    _inherit = 'account.payment'

    solde_final = fields.Float(string="Solde", readonly=True)
    @api.model
    def create(self, vals):
        # Agregar codigo de validacion aca
        # raise ValidationError(_(vals['partner_id']))
        myvals ={
            'date':vals['payment_date'],
            'type_operation':'1',
            'montant':vals['amount'],
            'solde': self.solde_final,
            'partner_id':vals['partner_id'],
            'state':'confirmed'
        }
        self.env['manifest.operation'].create(myvals)
        return super(AccountPayment, self).create(vals)
    
    @api.onchange('partner_id','amount')
    def _calcul_solde(self):
        for rec in self:
            solde = 0
            operations = self.env['manifest.operation'].search([('partner_id','=', rec.partner_id.id),('state','=','confirmed')])
            for op in operations:
                if op.type_operation == '0':
                    solde += op.montant
                else:
                    solde -= op.montant
            rec.solde_final = solde - rec.amount

