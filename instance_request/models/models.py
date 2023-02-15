# -*- coding: utf-8 -*-

from odoo import models, fields, api

class instance_request(models.Model):
     _name = 'instance.request'
     _description = 'Demande d\'instance'

     name = fields.Char()
     adress_ip = fields.Char()
     active = fields.Boolean(default=True)
     cpu = fields.Char()
     ram = fields.Char()
     disk = fields.Char()
     url = fields.Char()
     state = fields.Selection(['Brouillon', 'Soumise', 'En traitement', 'Traitee'],default='Brouillon')
     limit_date = fields.Date('Date limite de traitement')
     treat_date = fields.Datetime('Date de traitement')
     treat_duration = fields.Float(string="Duree de traitement")

     #@api.depends('value')
     #def _value_pc(self):
         #for record in self:
             #record.value2 = float(record.value) / 100
