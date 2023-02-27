# -*- coding: utf-8 -*-
from importlib.resources import _

from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    odoo_version_id = fields.Many2one("odoo.version", string="Odoo version")
    instance_ids = fields.One2many("instance.request", "tl_id", string="Instance creation requests", tracking=True)
    nb_instances = fields.Integer(string="Nb instances", compute="_compute_nb_instance_ids")

    def _compute_nb_instance_ids(self):
        for record in self:
            record.nb_instances = len(record.instance_ids)

    def employee_instance_requests(self):
        print(self.nb_instances)
        return {
            'name': _('Instance Requests'),
            'type': 'ir.actions.act_window',
            'res_model': 'instance.request',
            'view_mode': 'tree',
            'domain': [('tl_id', '=', self.id)]
        }
