# -*- coding: utf-8 -*-

from odoo import models, fields, api


class OdooVersion(models.Model):
    _name = "odoo.version"
    _description = "Versions de Odoo"

    name = fields.Char(string="Version")
    current_version = fields.Boolean(string="Current version")
    instance_ids = fields.One2many("instance.request", "odoo_version_id", string="Instances")
