# -*- coding: utf-8 -*-

from odoo import models, fields, api

class InstanceRequest(models.Model):
     _name = "instance.request"
     _description = "Instance request"

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
               # pointe sur le groupe, recuperer l'id du groupe
               user_group = self.env.ref('instance_request.group_manager')
               print("==========> groupe:  ", user_group)
               users = user_group.users

               for user in users:
                    print("======> name: ", user.name)

               user_connected = self.env.user
               print("==========> utilisateur connecté:  ", user_connected)
               has_user_group = user_connected.has_group('instance_request.group_manager')
               print("==========> Il appartient au groupe manager?  ", has_user_group)

               model_access = user_group.model_access
               print('============== model access =================')
               for access in model_access:
                    print("======> ", access.name, access.perm_create, access.perm_write, access.perm_read, access.perm_unlink)
     def action_done(self):
          for record in self:
               record.state = 'done'