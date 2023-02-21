# -*- coding: utf-8 -*-

from odoo import models, fields, api


class InstanceRequest(models.Model):
    _name = "instance.request"
    _description = "Instance request"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Designation", required=True, tracking=True)
    adress_ip = fields.Char(string="IP Address")
    active = fields.Boolean(string="Active", default=True)
    cpu = fields.Char(string="CPU")
    ram = fields.Char(string="RAM")
    disk = fields.Char(string="DisK")
    url = fields.Char(string="URL")
    limit_date = fields.Date(string="Processing deadline", tracking=True)
    treat_date = fields.Datetime(string="Processing date")
    treat_duration = fields.Float(string="Processing duration")
    state = fields.Selection([
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("in_process", "In process"),
        ("done", "Done")
    ], string="State", default="draft", tracking=True)

    def action_draft(self):
        for record in self:
            record.state = 'draft'
        template = self.env.ref('instance_request.instance_request_creation')
        template.send_mail(record.id,
                           email_values={'email_to': record.create_uid.email, 'email_from': self.env.user.email})

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
                print("======> ", access.name, access.perm_create, access.perm_write, access.perm_read,
                      access.perm_unlink)

    def action_done(self):
        for record in self:
            record.state = 'done'
            record.activity_feedback(['instance_request.instance_request_to_process_activity'])
            template = self.env.ref('instance_request.instance_request_instance_created')
            template.send_mail(record.id,
                               email_values={'email_to': record.create_uid.email, 'email_from': self.env.user.email})

    # def instance_request_to_process(self, init_values):
    #      self.ensure_one()
    #      if 'state' in init_values and (self.state == 'draft' or self.state == 'submitted'):
    #           return self.env.ref('my_module.mt_state_change')
    #      return super(InstanceRequest,self).instance_request_to_process(init_values)

