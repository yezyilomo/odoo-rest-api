# -*- coding: utf-8 -*-
import json
import math
import logging
import functools
import werkzeug
from collections import Counter
from datetime import datetime
from odoo import http, api, _
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import slug


class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class FormatError(Error):
    """Exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message


def check_if_instanceof(against, faulty_node):

    def wraper(node):
        result = isinstance(node, against)
        if not result and isinstance(faulty_node, list):
            faulty_node.append(str(node))
       
        return result
    return wraper


def isqueryable(obj, query, faulty_node=None):
    flat_or_nested = all(
        map(check_if_instanceof((str, dict), faulty_node), query)
    )
    
    iterable = (len(query) <= 1) and \
               all(
                   map(check_if_instanceof((list, tuple), faulty_node), query)
               )
               
    if not (flat_or_nested or iterable):
        faulty_node = "".join(faulty_node)
        return False
    else:
        return True


def _jsonify_obj(obj, query, call_callable, not_found_create, fields=None):
    faulty_node = []
       
    if not isqueryable(obj, query, faulty_node=faulty_node):
        raise FormatError(f"Wrong formating of Query on \"{faulty_node}\" field")
        
    for field in query:
        if isinstance(field, str):                      
            # Flat field
            if fields is None:
                     fields = {}
            if callable( getattr(obj, field) ) and call_callable:
                fields.update({field: getattr(obj, field)()})
            else:
                fields.update({field: getattr(obj, field)})
                
            
        elif isinstance(field, dict):
            # Nested field
            for sub_field in field:
                found = hasattr(obj, sub_field)
                
                # This cond below is for dict fields only
                # bcuz it's the only way to create new fields 
                if not_found_create and not found:
                    # Create new field 
                    fields.update({sub_field: field[sub_field]})
                    continue
                elif not found:
                    # Throw NotFound Error [FIXME]
                    getattr(obj, sub_field)
                    continue
                    
                    
                if len(field[sub_field]) < 1:
                    # Nested empty object, 
                    # Empty dict is the default value for empty nested objects.
                    # Comment the line below to remove empty objects in results. [FIXME]
                    fields.update({sub_field: {}}) 
                    continue
                    
                if isinstance(field[sub_field][0], (list, tuple)):
                    # Nested object is iterable
                    fields.update({sub_field: []})
                else:
                    # Nested object is flat
                    fields.update({sub_field: {}})
                    
                obj_field = getattr(obj, sub_field)
                if callable( obj_field ) and call_callable:
                    obj_field = obj_field()
                    
                _jsonify_obj(
                    obj_field,
                    field[sub_field], 
                    call_callable,
                    not_found_create,
                    fields=fields[sub_field],
                )
                
        elif isinstance(field, (list, tuple)):
            # Nested object
            if fields is None:
                     fields = []
            for sub_obj in obj:
                sub_field={}
                fields.append(sub_field)
                _jsonify_obj(
                    sub_obj, 
                    field, 
                    call_callable,
                    not_found_create,
                    fields=sub_field
                )
        else:
            raise Exception(
                f"""
                Wrong formating of Query on '{field}' field,
                It seems like the Query was mutated on run time, 
                Use 'tuple' instead of 'list' to avoid mutating Query accidentally.
                """
            )

    return fields


def jsonify(data, query, call_callable=False, not_found_create=False):
    return _jsonify_obj(data, query, call_callable, not_found_create)


    

class MifosIntegration(http.Controller):
    @http.route('/api/users/', auth='public')
    def sys_users(self, **kw):
        users = request.env['res.users'].sudo().search([])
        query = [[
            "id",
            "name",
            {
                "groups_id": [
                    [
                        "id",
                        "name"
                    ]
                ]
            }
        ]]
        data = jsonify(users, query)
        return http.Response(
            json.dumps(data),
            status=200,
            mimetype='application/json'
        )

    @http.route('/api/journals/', auth='public')
    def account_journals(self, **kw):
        journals = request.env['account.journal'].sudo().search([])
        query = [[
            "id",
            "name"
        ]]
        data = jsonify(journals, query)
        return http.Response(
            json.dumps(data),
            status=200,
            mimetype='application/json'
        )

    @http.route('/api/account-charts/', auth='public')
    def chart_of_account(self, **kw):
        accounts = request.env['account.account'].sudo().search([])
        query = [[
            "id",
            "name"
        ]]
        data = jsonify(accounts, query)
        return http.Response(
            json.dumps(data),
            status=200,
            mimetype='application/json'
        )
