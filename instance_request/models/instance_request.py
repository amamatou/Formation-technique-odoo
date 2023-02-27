# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import timedelta, date
import pprint
from odoo.exceptions import UserError, ValidationError


class InstanceRequest(models.Model):
    _name = "instance.request"
    _description = "Instance request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _sql_constraints = [
        ('unique_address_ip', 'unique (address_ip)', 'IP address already exists!'),
        # ('unique_name', 'unique (name)', 'Name already exists!')
    ]

    name = fields.Char(string="Designation", required=True, tracking=True, default="New")
    address_ip = fields.Char(string="IP Address")
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

    odoo_version_id = fields.Many2one("odoo.version", string="Odoo Version")
    # odoo_version_ids = fields.Many2many("odoo.version", string="Odoo Versions")
    requests_line_ids = fields.One2many("instance.request.line", "instance_id", string="Instance request line")

    nb_lines = fields.Integer(string="Nb Lines", compute="_compute_nb_lines", store=1)

    partner_id = fields.Many2one("res.partner", string="Client")
    tl_id = fields.Many2one("hr.employee", string="Employe")
    tl_user_id = fields.Many2one("", string="Utilisateur sur l'employe")

    color = fields.Selection(selection=[
        ('green', 'Green'),
        ('yellow', 'Yellow'),
        ('red', 'Red')], string="Color", default="red", tracking=True)

    @api.depends("requests_line_ids")
    def _compute_nb_lines(self):
        for record in self:
            record.nb_lines = len(record.requests_line_ids)

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
            user_group = self.env.ref('instance_request.instance_request_group_manager')
            print("==========> groupe:  ", user_group)
            users = user_group.users
            for user in users:
                print("======> name: ", user.name)

            user_connected = self.env.user
            print("==========> utilisateur connecté:  ", user_connected)
            has_user_group = user_connected.has_group('instance_request.instance_request_group_manager')
            print("==========> Il appartient au groupe manager?  ", has_user_group)

            model_access = user_group.model_access
            print('============== model access =================')
            for access in model_access:
                print("======> ", access.name, access.perm_create, access.perm_write, access.perm_read,
                      access.perm_unlink)

            remaining_days = record.limit_date - date.today()
            users = self.env.ref('instance_request.instance_request_group_manager').users
            for user in users:
                self.activity_schedule(
                    'instance_request.instance_request_to_process_activity',
                    note=('Instance request in process, deadline in %s days.' % (remaining_days)),
                    user_id=user.id
                )
            # self.activity_schedule(
            #     'mail.mail_activity_data_meeting',
            #     summary='This is an automatically generated activitty',
            #     note='Some meeting you have to attend',
            #     date_deadline=datetime.datetime.today() + datetime.timedelta(days=5),
            #     user_id=self.env.user.id
            # )

    def action_done(self):
        for record in self:
            if not record.limit_date:
                raise ValidationError("You can't done a request without a processing deadline")
            record.state = 'done'
            record.activity_feedback(['instance_request.instance_request_to_process_activity'])
            template = self.env.ref('instance_request.instance_request_instance_created')
            template.send_mail(record.id,
                               email_values={'email_to': record.create_uid.email, 'email_from': self.env.user.email})
            # try:
            #     raise UserError("")
            # except Exception as ex:
            #     pass

    @api.model
    def set_submit_with_limit_date(self):
        allrecords = self.search([])
        for record in allrecords:
            if (record.limit_date - timedelta(days=5)) <= date.today() < (
                    record.limit_date + timedelta(days=6)) and record.state == "draft":
                record.state = "submitted"

    @api.model_create_multi
    def create(self, vals_list):
        print("================ vals_list ===================")
        pprint.pprint(vals_list)

        for val in vals_list:
            val['cpu'] = 8
            print("========> vals ", val)
            if val['name'] == 'New':
                val['name'] = 'INST' + self.env['ir.sequence'].next_by_code('instance.request')

        records = super().create(vals_list)
        print("========> records ", records)

        for rec in records:
            print("========> RAM before ", rec.ram)
            rec.ram = 16
            print("========> RAM after ", rec.ram)

        return records

    @api.onchange('treat_duration')
    def increase_treat_date(self):
        for record in self:
            if record.treat_date:
                record.treat_date = record.treat_date + timedelta(hours=record.treat_duration)

    # depends agit apres la sauvegarde
    # constraints agit avant la sauvegarde

    @api.onchange('limit_date')
    def limit_date_exception(self):
        for record in self:
            if record.limit_date != False and date.today() > record.limit_date:
                raise UserError('Vous ne pouvez pas définir une date limite postérieure à aujourd’hui.')

    @api.depends('limit_date')
    def limit_date_activity(self):
        for record in self:
            remaining_days = record.limit_date - date.today()
            users = self.env.ref('instance_request.instance_request_group_manager').users
            for user in users:
                self.activity_schedule(
                    'instance_request.instance_request_to_process_activity',
                    note=('processing deadline have been changed, deadline in %s days.' % (remaining_days)),
                    user_id=user.id
                )

    def unlink(self):
        for record in self:
            if record.state != 'draft':
                raise UserError('Vous ne pouvez supprimer que les demande d’instance en état Brouillon.')
        return super(InstanceRequest, self).unlink()
