# -*- coding: utf-8 -*-

from odoo import models, fields, api


class InstanceRequest(models.Model):
    _inherit = "instance.request"

    cpu = fields.Char(string="CPU")


class InheritTwoInstanceRequest(models.Model):
    _name = "inherit.two.instance.request"  # Nouvelle table
    _inherit = "instance.request"

    cpu = fields.Char(string="CPU")  # new field


class InheritThreeInstanceRequest(models.Model):
    _name = "inherit.three.instance.request"  # Nouvelle table
    _inherit = {"instance.request": "instance_id"}

    attachment_id = fields.Many2one('ir.attachment',
                                    required=True,
                                    string='Attachment',
                                    ondelete='cascade') #relationship with the model inherited
