# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

from odoo.addons.instance_request.models.instance_request import InstanceRequest


class InstanceBonWizard(models.TransientModel):
    _name = "instance.bon.wizard"
    _description = "Instance purchase order wizard"

    sale_order_ids = fields.Many2many("sale.order", string="Sale orders")
    cpu = fields.Char(string="CPU")
    ram = fields.Char(string="RAM")
    disk = fields.Char(string="DisK")
    tl_id = fields.Many2one("hr.employee", string="Employee")

    @api.model
    def create_instance(self):
        for record in self:
            if record.cpu <= record.ram <= record.disk < 0 or record.cpu == record.ram == record.disk == False:
                raise ValidationError("You can't ask for instance requests with zero performances !")
            list_instances_created = []
            for sale_order in record.sale_order_ids:
                vals = [{
                    'name': self.env['ir.sequence'].next_by_code('instance.request.sequence') + sale_order.name,
                    'limit_date': sale_order.date_order,
                    'cpu': record.cpu,
                    'ram': record.ram,
                    'disk': record.disk
                }]
                # list_instances_created.append(super(InstanceRequest, self).create(vals))
                instance_created = self.env['instance.request'].create(vals)
                list_instances_created.append(instance_created.id)
            return list_instances_created

    def redirect_create_instance(self):
        list_instance_ids = self.create_instance()
        print(list_instance_ids)
        return {
            'name': 'Instance Requests',
            'type': 'ir.actions.act_window',
            'res_model': 'instance.request',
            'view_mode': 'tree',
            'domain': [('id', 'in', list_instance_ids)]
        }
