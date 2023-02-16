# -*- coding: utf-8 -*-

from odoo import models, fields, api

class instance_request(models.Model):
     _name = "instance.request"
     _description = "Demande d'instance"

     name = fields.Char(string="Designation")
     adress_ip = fields.Char(string="Addresse IP")
     active = fields.Boolean(string="Active",default=True)
     cpu = fields.Char(string="CPU")
     ram = fields.Char(string="RAM")
     disk = fields.Char(string="Disque")
     url = fields.Char(string="URL")
     state = fields.Selection([
          ("brouillon","Brouillon"),
          ("soumise", "Soumise"),
          ("en_traitement", "En traitement"),
          ("traitee","Traitee")
     ],string="Statut",default="Brouillon")
     limit_date = fields.Date(string="Date limite de traitement")
     treat_date = fields.Datetime(string="Date de traitement")
     treat_duration = fields.Float(string="Duree de traitement")

     #@api.depends('value')
     #def _value_pc(self):
         #for record in self:
             #record.value2 = float(record.value) / 100
