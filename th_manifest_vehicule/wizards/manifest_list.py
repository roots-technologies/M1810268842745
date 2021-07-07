# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ManifestList(models.TransientModel):
    _name = 'manifest.list'
    _description = "Impression de la liste de manifests"

    date_debut = fields.Date(string="Date de début",
                             default=fields.date.today(),)
    date_fin = fields.Date(string="Date de fin", default=fields.date.today(),)
    partner_id = fields.Many2one(
        'res.partner',
        string='Importateur',
    )
    navire_id = fields.Many2one(
        'manifest.navire',
        string='Navire',
    )

    def imprimer_liste_manifest(self):
        data = {}
        liste_manifest = []
        manifests = self.env['manifest.manifest'].search(
            [('date_arrive', '>=', self.date_debut), ('date_arrive', '<=', self.date_fin)])
        if self.partner_id:
            manifests = self.env['manifest.manifest'].search(
                [('date_arrive', '>=', self.date_debut), ('date_arrive', '<=', self.date_fin), ('partner_id', '=', self.partner_id.id)])

        if self.navire_id:
            manifests = self.env['manifest.manifest'].search(
                [('date_arrive', '>=', self.date_debut), ('date_arrive', '<=', self.date_fin), ('navire_id', '=', self.navire_id.id)])

        if self.navire_id and self.partner_id:
            manifests = self.env['manifest.manifest'].search(
                [('date_arrive', '>=', self.date_debut), ('date_arrive', '<=', self.date_fin),  ('partner_id', '=', self.partner_id.id), ('navire_id', '=', self.navire_id.id)])

        for m in manifests:
            vehicule_ids = []
            for v in m.vehicule_ids:
                vals = {
                    'product_id': v.product_id.name,
                    'chassis': v.chassis,
                    'numero_bl': v.numero_bl,
                    'poids': v.poids,
                }
                vehicule_ids.append(vals)
            vals = {
                'navire_id': m.navire_id.name,
                'date_arrive': m.date_arrive,
                'partner_id': m.partner_id.name,
                'vehicule_ids': vehicule_ids,
            }
            liste_manifest.append(vals)
        data['liste_manifest'] = liste_manifest
        return self.env.ref('th_manifest_vehicule.th_manifest_list_report_view').report_action(self, data=data)
