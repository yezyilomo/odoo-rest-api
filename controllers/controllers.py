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

    @http.route('/api/model/', auth='public')
    def chart_of_account(self, **kwargs):
        model = kwargs["name"]
        query = json.loads(kwargs["query"])
        accounts = request.env[model].sudo().search([])
        data = dictfier.dictfy(accounts, query)
        return http.Response(
            json.dumps(data),
            status=200,
            mimetype='application/json'
        )
