# -*- coding: utf-8 -*-
import json
import math
import logging
import werkzeug
import dictfier
from odoo import http, api, _
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import slug


class MifosIntegration(http.Controller):

    @http.route('/api/model/', auth='public', methods=['GET'], csrf=False)
    def get_model_data(self, **kwargs):
        model = kwargs["name"]
        query = json.loads(kwargs["query"])
        accounts = request.env[model].sudo().search([])
        data = dictfier.dictfy(accounts, query)
        return http.Response(
            json.dumps(data),
            status=200,
            mimetype='application/json'
        )

    @http.route('/api/model/', type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def post_model_data(self, **post):
        model = post["model"]
        data = request.env[model].sudo().create(post["data"])
        return data
