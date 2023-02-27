# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Perimeters(models.Model):
    _name = "perimeters"
    _description = "Perimeters"

    name = fields.Char(string="Designation")
