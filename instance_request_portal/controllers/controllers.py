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
from odoo.tools import groupby as groupbyelem
from operator import itemgetter


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

    def _instance_get_groupby_mapping(self):
        return {
            'state': 'state'
        }

    def _prepare_instances_values(
            self, page=1, date_begin=None, date_end=None, sortby=None, filterby='all', search=None, search_in="all",
            groupby='none',
            quotation_page=False, **kwargs
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

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'partner_id': {'label': _('Customer'), 'domain': [("partner_id", "!=", False)]},
            'url': {'label': _('URL'), 'domain': [("url", "!=", False)]},
            'odoo_version_id': {'label': _('Odoo version'), 'domain': [("odoo_version_id", "!=", False)]},
        }

        searchbar_inputs = {
            'all': {'label': _('Search in all'), 'input': 'all'},
            'partner_id': {'label': _('Search in customer'), 'input': 'partner_id'},
            'url': {'label': _('Search in URL'), 'input': 'url'},
            'state': {'label': _('Search in state'), 'input': 'state'},
        }

        searchbar_groupby = {
            'none': {'label': _('None'), 'input': 'none'},
            'state': {'label': _('State'), 'input': 'state'},
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
            domain = AND([domain, self._get_search_domain(search_in, search)])

        # groupby
        # groupby_mapping = self._instance_get_groupby_mapping()
        # groupby_field = groupby_mapping.get(groupby, None)
        # if groupby_field is not None and groupby_field not in InstanceRequest.sudo()._fields:
        #     raise ValueError(_("The field '%s' does not exist in the targeted model", groupby_field))
        # sort_order = '%s, %s' % (groupby_field, sort_order) if groupby_field else sort_order

        # content according to pager and archive selected
        if groupby == 'state':
            sort_order = 'state, %s' % sort_order

        pager_values = portal_pager(
            url=url,
            total=InstanceRequest.search_count(domain),
            page=page,
            step=self._items_per_page,
            url_args={
                # 'date_begin': date_begin, 'date_end': date_end,
                'sortby': sortby, 'filterby': filterby, 'search_in': search_in, 'search': search
            },
        )
        instances = InstanceRequest.search(domain, order=sort_order, limit=self._items_per_page,
                                           offset=pager_values['offset'])

        if groupby == 'state':
            grouped_instances = [InstanceRequest.concat(*g)
                                 for k, g in groupbyelem(instances, itemgetter('state'))]
        else:
            grouped_instances = [instances]

        values.update({
            # 'date': date_begin,
            'instances': instances.sudo(),
            'grouped_instances': grouped_instances,
            'page_name': 'instances',
            'pager': pager_values,
            'default_url': url,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'searchbar_inputs': searchbar_inputs,
            'searchbar_groupby': searchbar_groupby,
            'sortby': sortby,
            'filterby': filterby,
            'search_in': search_in,
            'search': search,
            'groupby': groupby,
        })

        return values

    @http.route(['/my/instances', '/my/instances/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_instances(self, **kwargs):
        values = self._prepare_instances_values(quotation_page=True, **kwargs)
        return request.render("instance_request_portal.portal_my_instances", values)

    @http.route('/my/instances/create', auth='public', website=True)
    def create_instance(self, **kw):
        return http.request.render('instance_request_portal.create_instance', {})

    @http.route('/my/instances/create_request', auth='public', website=True)
    def create_request(self, **kwargs):
        request.env['instance.request'].sudo().create(kwargs)
        values = self._prepare_instances_values(quotation_page=True, **kwargs)
        return http.request.render('instance_request_portal.portal_my_instances', values)

    # @http.route(["/my/instances/<int:instance_id>/<access_token>"], type='http', auth="user", website=True)
    # def display_instance_form(self, instance_id=None):
    #     instance = request.env['instance.request'].sudo().search([('id', '=', instance_id)], limit=1)
    #     # print(instance.name)
    #     return http.request.render('instance_request_portal.display_instance_form_view', {
    #         'instance': instance,
    #         'instance_id': instance_id,
    #     })

    @http.route(['/my/instances/<model("instance.request"):instance_id>'], type='http', auth='public', website=True)
    def display_instance_form(self,instance_id, **kwargs):
        values = {'instance': instance_id, 'page_name':'instances_form_view'}
        return http.request.render('instance_request_portal.display_instance_form_view', values)
    @http.route(['/my/instances/update/<int:instance_id>', '/my/instances/update/'],
                auth='public', website=True)
    def update_request(self, instance_id=None, **kwargs):
        data = {
            'limit_date': kwargs.get('limit_date'),
            'ram': kwargs.get('ram'),
            'url': kwargs.get('url'),
            'disk': kwargs.get('disk'),
        }
        request.env['instance.request'].sudo().browse(instance_id).write(data)
        create_id = request.env.context.get('uid')
        instances = http.request.env['instance.request'].search([('create_uid', '=', create_id)])
        return http.request.render('instance_request_portal.portal_my_instances', {
            'instances': instances,
        })

    @http.route(['/my/instances/delete/<int:instance_id>'],
                auth='public', website=True)
    def delete_request(self, instance_id=None, **kw):
        request.env['instance.request'].sudo().browse(instance_id).unlink()
        print('deleting succeeded')

        create_id = request.env.context.get('uid')
        instances = http.request.env['instance.request'].search([('create_uid', '=', create_id)])
        return http.request.render('instance_request_portal.portal_my_instances', {
            'instances': instances,

        })
