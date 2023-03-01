# -*- coding: utf-8 -*-

from odoo import models, fields, api


class InstanceToDraftWizard(models.TransientModel):
    _name = "instance.to.draft.wizard"
    _description = "Instance to draft wizard"

    instance_ids = fields.Many2many("instance.request", string="Instances")

    def set_to_draft(self):
        for instance in self.instance_ids:
            instance.state = 'draft'
