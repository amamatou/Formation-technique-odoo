# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import binascii
from collections import OrderedDict

from odoo import fields, http, SUPERUSER_ID, _
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.fields import Command
from odoo.http import request

from odoo.addons.payment.controllers import portal as payment_portal
from odoo.addons.payment import utils as payment_utils
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.osv.expression import OR, AND


class CustomerPortal(portal.CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)

        InstanceRequest = request.env['instance.request']
        if 'instances_count' in counters:
            values['instances_count'] = InstanceRequest.search_count([('create_uid', '=', request.env.user.id)]) \
                if InstanceRequest.check_access_rights('read', raise_exception=False) else 0

        return values

    def _get_search_domain(self, search_in, search):
        search_domain = []
        if search_in in ('partner_id', 'all'):
            search_domain = OR([search_domain, [('partner_id', 'ilike', search)]])
        if search_in in ('url', 'all'):
            search_domain = OR([search_domain, [('url', 'ilike', search)]])
        if search_in in ('state', 'all'):
            search_domain = OR([search_domain, [('state', 'ilike', search)]])
        return search_domain

    def _prepare_instances_values(
            self, page=1, date_begin=None, date_end=None, filterby='all', sortby=None, search=None, search_in='all',
            quotation_page=False, **kwargs
        ):
        values = self._prepare_portal_layout_values()
        InstanceRequest = request.env['instance.request']

        url = "/my/instances"
        domain = [('create_uid', '=', request.env.user.id)]

        # if date_begin and date_end:
        #     domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        searchbar_sortings = {
            'limit_date': {'label': _('Limit Date'), 'order': 'limit_date asc'},
            'name': {'label': _('Designation'), 'order': 'name'},
            'state': {'label': _('State'), 'order': 'state'},
        }

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'partner_id': {'label': _('Customer'), 'domain': [("partner_id", "!=", False)]},
            'url': {'label': _('URL'), 'domain': [("url", "!=", False)]},
            'state': {'label': _('State'), 'domain': [("state", "!=", False)]},
        }

        searchbar_inputs = {
            'all': {'input': 'all', 'label': _('Search in All')},
            'partner_id': {'label': _('Search in Customer'), 'input': 'partner_id'},
            'url': {'label': _('Search in URL'), 'input': 'url'},
            'state': {'label': _('Search in State'), 'input': 'state'}
        }

        # default sort by value
        if not sortby:
            sortby = 'name'
        sort_order = searchbar_sortings[sortby]['order']

        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        # search
        if search and search_in:
            domain += self._get_search_domain(search_in, search)

        pager_values = portal_pager(
            url=url,
            total=InstanceRequest.search_count(domain),
            page=page,
            step=self._items_per_page,
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby, 'search_in': search_in, 'search': search},
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
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'searchbar_inputs': searchbar_inputs,
            'sortby': sortby,
            'filterby': filterby,
            'search_in': search_in,
            'search': search,
        })

        return values


@http.route(['/my/instances', '/my/instances/page/<int:page>'], type='http', auth="user", website=True)
def portal_my_instances(self, **kwargs):
    values = self._prepare_instances_values(quotation_page=True, **kwargs)
    return request.render("instance_request_portal.portal_my_instances", values)
