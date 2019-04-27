# -*- coding: utf-8 -*-
import json
import math
import logging
import datetime
import werkzeug

from odoo import http, api, _
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import slug

_logger = logging.getLogger(__name__)

try:
    import dictfier
except ImportError as err:
    _logger.debug(err)

import pprint
def flat_obj(obj, parent_obj, field_name):
    if isinstance(obj, datetime.datetime):
        return obj.strftime("%Y-%m-%d-%H-%M")
    if isinstance(obj, datetime.date):
        return obj.strftime("%Y-%m-%d")
    if isinstance(obj, datetime.time):
        return obj.strftime("%H-%M-%S")

    if hasattr(parent_obj, "fields_get"):
        field_type = parent_obj.fields_get(field_name)[field_name]["type"]
        if field_type == "many2one":
            return obj.id
        if field_type in ["one2many", "many2many"]:
            return [rec.id for rec in obj]
        if field_type == "binary" and obj:
            return obj.decode("utf-8")
  
    return obj

def nested_flat_obj(obj, parent_obj):
    return obj

def nested_iter_obj(obj, parent_obj):
    return obj

class OdooAPI(http.Controller):
    @http.route(
        '/api/', 
        auth='public', methods=['GET'], csrf=False)
    def get_model_data(self, **params):
        model = params["model"]

        records = request.env[model].sudo().search([])

        if "query" in params:
            query = json.loads(params["query"])
        else:
            query = [records.fields_get_keys()]
        
        if "exclude" in params:
            exclude = json.loads(params["exclude"])
            for field in exclude:
                if field in query[0]:
                    field_to_exclude= query[0].index(field)
                    query[0].pop(field_to_exclude)
        
        if "filter" in params:
            filters = json.loads(params["filter"])
            records = request.env[model].sudo().search(filters)

        prev_page = None
        next_page = None
        total_page_number = 1

        if "page_size" in params:
            page_size = int(params["page_size"])
            count = len(records)
            total_page_number = math.ceil(count/page_size)

            if "page" in params:
                page_number = int(params["page"])
            else:
                page_number = 1  # Default page Number

            records = records[page_size*(page_number-1):page_number*page_size]
            next_page = page_number+1 if 0<page_number+1 <= total_page_number else None
            prev_page = page_number-1 if 0<page_number-1 <= total_page_number else None

        if "limit" in params:
            limit = int(params["limit"])
            records = records[0:limit]
        data = dictfier.dictfy(
            records, 
            query,
            flat_obj=flat_obj,
            nested_flat_obj=nested_flat_obj,
            nested_iter_obj=nested_iter_obj
        )

        res = {
            "jsonrpc": "2.0",
            "id": None,
            "count": len(records),
            "prev": prev_page,
            "next": next_page,
            "total_pages": total_page_number,
            "result": data
        }
        return http.Response(
            json.dumps(res),
            status=200,
            mimetype='application/json'
        )

    @http.route(
        '/api/', 
        type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def post_model_data(self, **post):
        model = post["model"]
        if "context" in post:
            data = request.env[model].with_context(**post["context"]).sudo().create(post["data"])
        else:
            data = request.env[model].sudo().create(post["data"])
        return data.id

    @http.route(
        '/api/', 
        type='json', auth="public", methods=['PUT'], website=True, csrf=False)
    def put_model_data(self, **post):
        model = post["model"]
        filters = post["filter"]
        rec = request.env[model].sudo().search(filters)

        if "context" in post:
            rec = request.env[model].with_context(**post["context"]).sudo().search(filters)
        else:
            rec = request.env[model].sudo().search(filters)

        if rec.exists():
            return rec.write(post["data"])
        else:
            return False

    @http.route(
        '/api/', 
        type='http', auth="public", methods=['DELETE'], website=True, csrf=False)
    def delete_model_data(self, **post):
        model = post["model"]
        filters = json.loads(post["filter"])
        rec = request.env[model].sudo().search(filters)
        if rec.exists():
            is_deleted = rec.unlink()
        else:
            is_deleted = False
        res = {
            "jsonrpc": "2.0",
            "id": None,
            "result": json.dumps(is_deleted)
        }
        return http.Response(
            json.dumps(res),
            status=200,
            mimetype='application/json'
        )
