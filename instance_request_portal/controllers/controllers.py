# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import binascii

from odoo import fields, http, SUPERUSER_ID, _
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.fields import Command
from odoo.http import request

from odoo.addons.payment.controllers import portal as payment_portal
from odoo.addons.payment import utils as payment_utils
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import pager as portal_pager


class CustomerPortal(portal.CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id

        InstanceRequest = request.env['instance.request']
        if 'instances_count' in counters:
            values['instances_count'] = InstanceRequest.search_count([('create_uid', '=', request.env.user.id)]) \
                if InstanceRequest.check_access_rights('read', raise_exception=False) else 0

        return values

    def _prepare_instances_values(
            self, page=1, date_begin=None, date_end=None, sortby=None, quotation_page=False, **kwargs
    ):
        InstanceRequest = request.env['instance.request']

        if not sortby:
            sortby = 'name'
        values = self._prepare_portal_layout_values()
        url = "/my/instances"
        domain = [('create_uid', '=', request.env.user.id)]

        searchbar_sortings = {
            'limit_date': {'label': _('Limit Date'), 'order': 'limit_date desc'},
            'name': {'label': _('Designation'), 'order': 'name'},
            'state': {'label': _('State'), 'order': 'state'},
        }
        sort_order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        pager_values = portal_pager(
            url=url,
            total=InstanceRequest.search_count(domain),
            page=page,
            step=self._items_per_page,
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
        )
        instances = InstanceRequest.search(domain, order=sort_order, limit=self._items_per_page,
                                           offset=pager_values['offset'])

        values.update({
            'date': date_begin,
            'instances': instances.sudo(),
            'page_name': 'instances',
            'pager': pager_values,
            'default_url': url,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })

        return values

    @http.route(['/my/instances', '/my/instances/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_instances(self, **kwargs):
        values = self._prepare_instances_values(quotation_page=True, **kwargs)
        return request.render("instance_request_portal.portal_my_instances", values)
