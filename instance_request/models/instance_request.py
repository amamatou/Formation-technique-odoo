# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import timedelta, date, datetime
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

    name = fields.Char(string="Designation", tracking=True, default="New")
    address_ip = fields.Char(string="IP Address")
    active = fields.Boolean(string="Active", default=True)
    cpu = fields.Char(string="CPU")
    ram = fields.Char(string="RAM")
    disk = fields.Char(string="DisK")
    url = fields.Char(string="URL")
    limit_date = fields.Date(string="Processing deadline", tracking=True)
    treat_date = fields.Datetime(string="Processing date")
    treat_duration = fields.Float(string=_("Processing duration"), compute="_compute_treat_duration")
    state = fields.Selection([
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("in_process", "In process"),
        ("done", "Done")
    ], string="State", default="draft", tracking=True)

    odoo_version_id = fields.Many2one("odoo.version", string="Odoo Version")
    odoo_version_ids = fields.Many2many("odoo.version", string="Odoo Versions")
    requests_line_ids = fields.One2many("instance.request.line", "instance_id", string="Instance request line")

    nb_lines = fields.Integer(string="Nb Lines", compute="_compute_nb_lines", store=1)

    partner_id = fields.Many2one("res.partner", string="Customer")
    tl_id = fields.Many2one("hr.employee", string="Employee")
    tl_user_id = fields.Many2one(related="tl_id.user_id")
    perimeters_ids = fields.Many2many("perimeters", string="Perimeters")

    color = fields.Selection(selection=[
        ('green', 'Green'),
        ('yellow', 'Yellow'),
        ('red', 'Red'),
        ('black', 'Black')], string="Color", default="black", tracking=True)

    activity_bool = False

    @api.depends("requests_line_ids")
    def _compute_nb_lines(self):
        for record in self:
            record.nb_lines = len(record.requests_line_ids)

    def _compute_treat_duration(self):
        for record in self:
            record.treat_duration = (record.limit_date - date.today()).days

    def action_draft(self):
        for record in self:
            record.state = 'draft'

    def action_submit(self):
        for record in self:
            if record.state == 'draft':
                template = self.env.ref('instance_request.instance_request_creation')
                template.send_mail(record.id,
                                   email_values={'email_to': record.create_uid.email,
                                                 'email_from': self.env.user.email})
            get_if_submit = self.env.context.get('get_if_submit', False)
            print("==========>  ", get_if_submit)
            record.state = 'submitted'
            self.activity_unlink(['instance_request.instance_request_to_process_activity'])

    @api.model
    def action_progress_rpc(self, vals):
        self = self.browse(vals)
        self.action_progress
        return True

    def action_progress(self):
        for record in self:
            record.state = 'in_process'
            # remaining_days = record.limit_date - date.today()
            users = self.env.ref('instance_request.instance_request_group_manager').users
            for user in users:
                self.activity_schedule(
                    'instance_request.instance_request_to_process_activity',
                    note='Instance request in process',
                    user_id=user.id,
                    date_deadline=record.limit_date
                )
            # point on the group, retrieve the id of the group
            # user_group = self.env.ref('instance_request.instance_request_group_manager')
            # print("==========> group:  ", user_group)
            # users = user_group.users
            # for user in users:
            #     print("======> name: ", user.name)

            # user_connected = self.env.user
            # print("==========> user connected:  ", user_connected)
            # has_user_group = user_connected.has_group('instance_request.instance_request_group_manager')
            # print("==========> He belongs to the group manager?  ", has_user_group)

        # model_access = user_group.model_access
        # print('============== model access =================')
        # for access in model_access:
        #     print("======> ", access.name, access.perm_create, access.perm_write, access.perm_read,
        #           access.perm_unlink)

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
        all_records = self.search([])
        for record in all_records:
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

            if not val['name']:
                raise UserError('Name of sequence is required !')

            if val['name'] == 'New':
                val['name'] = self.env['ir.sequence'].next_by_code('instance.request.sequence')

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
                record.treat_date = record.treat_date + timedelta(days=record.treat_duration)

    # depends acts after the backup
    # constraints acts before the backup

    @api.onchange('limit_date')
    def limit_date_exception(self):
        for record in self:
            if record.limit_date:
                if date.today() > record.limit_date:
                    raise UserError("You can't define a limit date before today !")

    @api.onchange('limit_date')
    def limit_date_activity(self):
        for record in self:
            record.activity_reschedule(
                ['instance_request.instance_request_to_process_activity'],
                date_deadline=record.limit_date
            )

    def unlink(self):
        for record in self:
            if record.state != 'draft':
                raise UserError("You can only delete instance requests with draft state !")
        return super(InstanceRequest, self).unlink()
