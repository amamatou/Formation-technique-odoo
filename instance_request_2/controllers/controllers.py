# -*- coding: utf-8 -*-
# from odoo import http


# class InstanceRequest(http.Controller):
#     @http.route('/instance_request/instance_request', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/instance_request/instance_request/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('instance_request.listing', {
#             'root': '/instance_request/instance_request',
#             'objects': http.request.env['instance_request.instance_request'].search([]),
#         })

#     @http.route('/instance_request/instance_request/objects/<model("instance_request.instance_request"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('instance_request.object', {
#             'object': obj
#         })
