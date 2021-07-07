# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ManifestList(models.TransientModel):
    _name = 'manifest.financial.report'
    _description = "Impression de la liste de manifests"

    date_debut = fields.Date(string="Date de début",
                             default=fields.date.today(),)
    date_fin = fields.Date(string="Date de fin", default=fields.date.today(),)

    def imprimer_rapport_financier(self):
        data = {}
        liste_de_rapport = []
        vehicules = self.env['manifest.vehicule'].search([])
        factures = self.env['account.move'].search([])
        for v in vehicules:
            vals = {
                'designation': v.product_id.name,
                'chassis': v.chassis,
                'navire': v.manifest_id.navire_id.name,
                'categorie': v.categorie_id.name,
                'importateur': v.manifest_id.partner_id.name,
                }
            liste_de_rapport.append(vals)
        raise ValidationError(_(liste_de_rapport))
        return self.env.ref('th_manifest_vehicule.th_manifest_financial_report_view').report_action(self, data=data)
