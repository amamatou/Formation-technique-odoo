# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class InstanceBonWizard(models.TransientModel):
    _name = "instance.bon.wizard"
    _description = "Instance purchase order wizard"

    sale_order_ids = fields.Many2many("sale.order", string="Sale orders")
    name = fields.Char(string="")
    cpu = fields.Char(string="CPU")
    ram = fields.Char(string="RAM")
    disk = fields.Char(string="DisK")
    tl_id = fields.Many2one("hr.employee", string="Employee")

    @api.model
    def create_instance(self):
        for record in self:
            if record.cpu <= record.ram <= record.disk < 0:
                raise ValidationError("Vous ne pouvez pas demander des instannces avec des performances nulles !")
            return super('instance.request', self).create()

    def redirect_create_instance(self):
        self.create_instance()
        return {
            'name': 'Instance Requests',
            'type': 'ir.actions.act_window',
            'res_model': 'instance.request',
            'view_mode': 'tree',
            'domain': [('tl_id', '=', self.tl_id)]
        }
