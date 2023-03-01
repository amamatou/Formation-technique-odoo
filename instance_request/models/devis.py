# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Devis(models.Model):
    _inherit = "sale.order"

    version_odoo_id = fields.Many2one("odoo.version", string="Odoo version")

