from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError


class ManifestManifest(models.Model):

    _name = 'manifest.manifest'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Manifiest'

    name = fields.Char(string="Référence", readonly=True,
                       required=True, copy=False, default='Nouveau')
    navire_id = fields.Many2one(
        'manifest.navire',
        string='Navire',
        required=True, track_visibility='always'
    )
    date_arrive = fields.Date(string="Date d'arrivée", required=True, default=fields.date.today(),)
    partner_id = fields.Many2one(
        'res.partner',
        string='Importateur',
        required=True, track_visibility='always'
    )
    vehicule_ids = fields.One2many(
        'manifest.vehicule', 'manifest_id', string="Véhicules", required=True, track_visibility='always')

    state = fields.Selection(
        [('draft', 'Brouillon'), ('confirmed', 'Confirmer'),
         ('delivered', 'Livré'), ('accounted', 'Facturé'), ('canceled', 'Annulé')], default='draft', readonly=True, track_visibility='onchange',)

    def confrmer_manifest(self):
        for rec in self:
            rec.state = 'confirmed'

    def marque_livre(self):
        for rec in self:
            rec.state = 'delivered'

    def marque_annule(self):
        for rec in self:
            if rec.state == 'delivered' or rec.state == 'accounted':
                raise ValidationError(
                    _('Vous ne pouvez pas annuler un manifest comptabilisé ou délivré !'))
            rec.state = 'canceled'

    def marque_brouillon(self):
        for rec in self:
            rec.state = 'draft'

    def comptabiliser(self):
        lines = []
        for line in self.vehicule_ids:
            l = (0, 0, {
                'product_id': line.product_id.id,
                'name': line.marque_id,
                'price_unit': line.categorie_id.prix
            })
            lines.append(l)
        vals = {
            'partner_id': self.partner_id.id,
            'journal_id': 1,
            'type': 'out_invoice',
            'invoice_line_ids': lines,
            'manifest_id': self.id,
            'invoice_origin': self.name,
        }
        self.env['account.move'].create(vals)
        self.state = 'accounted'

    @api.model
    def create(self, vals):
        if vals.get('name', 'Nouveau') == 'Nouveau':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'manifest.manifest') or 'Nouveau'
            result = super(ManifestManifest, self).create(vals)
        return result


class ManifestVehicule(models.Model):

    _name = 'manifest.vehicule'
    _description = 'Vehicule'

    product_id = fields.Many2one(
        'product.product',
        string='Véhicule',
        required=True
    )
    marque_id = fields.Char(string="Marque de la voiture")
    type_vehicule_id = fields.Many2one(
        'manifest.type.vehicule',
        string='Type',
    )
    chassis = fields.Char(string="Chassis", required=True)
    categorie_id = fields.Many2one(
        'vehicule.categorie',
        string='Categorie',
        required=True
    )
    manifest_id = fields.Many2one(
        'manifest.manifest',
        string='Manifest',
    )
    numero_bl = fields.Char(string="Numéro du BL", required=True)
    poids = fields.Float(string="Poids")
    
    status = fields.Selection([('disponible', 'Disponible'),('retire','Retiré')], default='disponible')

    @api.onchange('product_id')
    def onchange_product_id(self):
        for rec in self:
            self.marque_id = self.product_id.display_name


class ManifestMarque(models.Model):

    _name = 'manifest.marque'
    _description = 'Marque de voiture'

    name = fields.Char(string="Nom de la marque")


class ManifestTypeVehicule(models.Model):

    _name = 'manifest.type.vehicule'
    _description = 'Type de véhicule'

    name = fields.Char(string="Nom du type")


class VehiculeCategorie(models.Model):

    _name = 'vehicule.categorie'
    _description = 'Catégorie de véhicule'

    name = fields.Char(string="Nom de la catégorie")
    poids_min = fields.Float(string="Poids minimum")
    poids_max = fields.Float(string="Poids maximum")
    prix = fields.Float(string="Prix")


class ManifestNavire(models.Model):

    _name = 'manifest.navire'
    _description = 'Navire'

    name = fields.Char(string="Nom de la navire")


class AccountMoveInherit(models.Model):

    _inherit = 'account.move'

    manifest_id = fields.Many2one(
        'manifest.manifest',
        string='Manifest',
    )


class ProductProductInherit(models.Model):

    _inherit = 'product.product'

    categorie_id = fields.Many2one(
        'vehicule.categorie',
        string='Catégorie',
    )
    vehicule_type_id = fields.Many2one(
        'manifest.type.vehicule',
        string='Type de véhicule',
    )
    dispo_en_manifest = fields.Boolean(string="Disponible en manifest")
    marque_vehicule = fields.Char(string="Marque de véhicule")

class ProductTemplateInherit(models.Model):

    _inherit = 'product.template'

    categorie_id = fields.Many2one(
        'vehicule.categorie',
        string='Catégorie',
    )
    vehicule_type_id = fields.Many2one(
        'manifest.type.vehicule',
        string='Type de véhicule',
    )
    dispo_en_manifest = fields.Boolean(string="Disponible en manifest")
    marque_vehicule = fields.Char(string="Marque de véhicule")
