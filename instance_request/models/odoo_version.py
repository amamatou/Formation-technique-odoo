# -*- coding: utf-8 -*-

from odoo import models, fields, api

class OdooVersion(models.Model):
    _name = 'odoo.version'
    _description = 'Versions de Odoo'

    name = fields.Char('Version')