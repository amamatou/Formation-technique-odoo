# -*- coding: utf-8 -*-

from odoo import models, fields, api

class InstanceRequest(models.Model):
     _name = "instance.request"
     _description = "Demande d'instance"

     name = fields.Char(string="Designation")
     adress_ip = fields.Char(string="IP Address")
     active = fields.Boolean(string="Active",default=True)
     cpu = fields.Char(string="CPU")
     ram = fields.Char(string="RAM")
     disk = fields.Char(string="DisK")
     url = fields.Char(string="URL")
     limit_date = fields.Date(string="Processing deadline")
     treat_date = fields.Datetime(string="Processing date")
     treat_duration = fields.Float(string="Processing duration")
     state = fields.Selection([
          ("draft","Draft"),
          ("submitted","Submitted"),
          ("in_process","In process"),
          ("done","Done")
     ],string="State",default="draft")


     def action_draft(self):
          for record in self:
               record.state = 'draft'

     def action_submit(self):
          for record in self:
               get_if_submit = self.env.context.get('get_if_submit', False)
               print("==========>  ", get_if_submit)
               record.state = 'submitted'

     def action_progress(self):
          for record in self:
               record.state = 'in_process'

     def action_done(self):
          for record in self:
               record.state = 'done'