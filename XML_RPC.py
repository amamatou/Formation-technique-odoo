# -*- coding: utf-8 -*-
from pprint import pprint
# import xmlrpc.client as xmlrpclib
from xmlrpc import client as xmlrpclib

url = "http://localhost:8016"
db = "odoo16"
username = "admin"
password = "admin"

common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url), allow_none=True)
uid = common.authenticate(db, username, password, {})
if uid:
    print("=====> success of authentication for the user ", uid)

    models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url), allow_none=True)

    ##Liste des instances
    # list_instances = models.execute_kw(db, uid, password, 'instance.request', 'search', [[]])
    # print("=====> List ids of instances", list_instances)
    #

    ##Liste des instances avec les champs spécifiés
    # list_instances_search_read = models.execute_kw(db, uid, password, 'instance.request', 'search_read', [[]],
    #                                                {'fields': ['name', 'limit_date', 'odoo_version_id'], })
    # print("=====> List of instances search and read")
    # pprint(list_instances_search_read)
    # for instance in list_instances_search_read:
    #     print("    ", instance)

    #Creation d'instances
    id = models.execute_kw(db, uid, password, 'instance.request', 'create', [{'name': 'Serveur FXX', 'limit_date': '2023-03-25', 'state': 'submitted'}])
    print("=====> Instance created", id)

    models.execute_kw(db, uid, password, 'instance.request', 'action_progress_rpc', [[id]])
    print("=====> Instance update, state set to progress", id)

else:
    print("=====> authentication failed")
