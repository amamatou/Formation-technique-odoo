# -*- coding: utf-8 -*-

from odoo import models, fields, api


class InstanceRequestLine(models.Model):
    _name = "instance.request.line"
    _description = "Instance Request Line"

    name = fields.Char(string="Designation")
    instance_id = fields.Many2one("instance.request", string="Instance request")
    odoo_version_id = fields.Many2one(related="instance_id.odoo_version_id")
