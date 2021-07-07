# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ManifestOperationCreate(models.TransientModel):
    _name = 'manifest.operation.wizard'
    _description = "Créer une opération"

    date_operation = fields.Date(string="Date",
                             default=fields.date.today(),)
    partner_id = fields.Many2one(
        'res.partner',
        string='Importateur',
    )
    solde_initial = fields.Float(string="Solde initial", readonly=True)
    solde_final = fields.Float(string="Solde du final", reaonly=True)
    type_operation = fields.Selection([('0', 'Dépôt'),('1','Retrait')],string="Type d'opération")
    montant = fields.Float(string="Montant")

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
            rec.solde_initial = solde - rec.montant

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
                rec.solde_final = solde + rec.montant
            else:
                rec.solde_final = solde - rec.montant

    def creer_operation(self):
        for rec in self:
            vals={
                'date':rec.date_operation,
                'type_operation':rec.type_operation,
                'montant':rec.montant,
                'solde':rec.solde_final,
                'partner_id':rec.partner_id.id,
                'state':'confirmed'
            }
            return self.env['manifest.operation'].create(vals)