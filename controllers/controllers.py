# -*- coding: utf-8 -*-
import json
import math
import logging
import functools
import werkzeug
import dictfier
from collections import Counter
from datetime import datetime
from odoo import http, api, _
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import slug


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
        data = dictfier.dictfy(users, query)
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
        data = dictfier.dictfy(journals, query)
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
        data = dictfier.dictfy(accounts, query)
        return http.Response(
            json.dumps(data),
            status=200,
            mimetype='application/json'
        )
