# -*- coding: utf-8 -*-
import json
import math
import logging
import werkzeug

from odoo import http, api, _
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import slug

_logger = logging.getLogger(__name__)

try:
    import dictfier
except ImportError as err:
    _logger.debug(err)

class OdooAPI(http.Controller):
    @http.route(
        '/api/model/', 
        auth='public', methods=['GET'], csrf=False)
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

    @http.route(
        '/api/model/', 
        type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def post_model_data(self, **post):
        model = post["model"]
        data = request.env[model].sudo().create(post["data"])
        return data.id

    @http.route(
        '/api/model/', 
        type='json', auth="public", methods=['PUT'], website=True, csrf=False)
    def put_model_data(self, **post):
        model = post["model"]
        rec_id = post["id"]
        rec = request.env[model].sudo().search([("id", "=", rec_id)])
        if rec.exists():
            return rec.write(post["data"])
        else:
            return False

    @http.route(
        '/api/model/', 
        type='json', auth="public", methods=['DELETE'], website=True, csrf=False)
    def delete_model_data(self, **post):
        model = post["model"]
        rec_id = post["id"]
        rec = request.env[model].sudo().search([("id", "=", rec_id)])
        if rec.exists():
            return rec.unlink()
        else:
            return False
