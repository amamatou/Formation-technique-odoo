# -*- coding: utf-8 -*-
from importlib.resources import _

from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    odoo_version_id = fields.Many2one("odoo.version", string="Odoo version")
    instance_ids = fields.One2many("instance.request", "tl_id", string="Instance requests")

    def employee_instance_requests(self):
        return {
            'name': _('Instance Requests'),
            'type': 'ir.actions.act_window',
            'res_model': 'instance.request',
            'view_mode': 'tree',
            'domain': [('tl_id', '=', self.id)]
        }
