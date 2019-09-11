# -*- coding: utf-8 -*-
import json
import math
import logging
import requests
import datetime

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

try:
    import dictfier
except ImportError as err:
    _logger.debug(err)


def flat_obj(obj, parent_obj, field_name):
    if isinstance(obj, datetime.datetime):
        return obj.strftime("%Y-%m-%d-%H-%M")
    if isinstance(obj, datetime.date):
        return obj.strftime("%Y-%m-%d")
    if isinstance(obj, datetime.time):
        return obj.strftime("%H-%M-%S")

    if hasattr(parent_obj, "fields_get"):
        field = parent_obj.fields_get(field_name)[field_name]
        field_type = field["type"]
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
    @http.route('/auth/', 
        type='json', auth='public',
        methods=["POST"], csrf=False, sitemap=False)
    def authenticate(self, *args, **post):
        login = post["login"]
        password = post["password"]
        try:
            db = request.env.cr.db
        except Exception:
            if "db" in post:
                db = post["db"]
            else:
                msg = (
                    "Looks like db is not properly configured, "
                    "you can pass its name to `db` parameter to "
                    "avoid this error!."
                )
                return {"Error": msg}

        url_root = request.httprequest.url_root
        AUTH_URL = f"{url_root}web/session/authenticate/"
        
        headers = {'Content-type': 'application/json'}
            
        data = {
            "jsonrpc": "2.0",
            "params": {
                "login": login,
                "password": password,
                "db": db
            }
        }
        
        res = requests.post(
            AUTH_URL, 
            data=json.dumps(data), 
            headers=headers
        )
        
        try:
            session_id = res.cookies["session_id"]
            user = json.loads(res.text)
            user["result"]["session_id"]= session_id
        except Exception:
            return "Invalid credentials."
        return user["result"]

    @http.route('/object/<string:model>/<string:function>', 
        type='json', auth='public',
        methods=["POST"], csrf=False, sitemap=False)
    def call_model_function(self, model, function, **post):
        args = []
        kwargs = {}
        if "args" in post:
            args = post["args"]
        if "kwargs" in post:
            kwargs = post["kwargs"]
        model = request.env[model]
        result = getattr(model, function)(*args, **kwargs)
        return result

    @http.route('/object/<string:model>/<int:rec_id>/<string:function>', 
        type='json', auth='public',
        methods=["POST"], csrf=False, sitemap=False)
    def call_obj_function(self, model, rec_id, function, **post):
        args = []
        kwargs = {}
        if "args" in post:
            args = post["args"]
        if "kwargs" in post:
            kwargs = post["kwargs"]
        obj = request.env[model].browse(rec_id).ensure_one()
        result = getattr(obj, function)(*args, **kwargs)
        return result

    @http.route(
        '/api/<string:model>', 
        auth='user', methods=['GET'], csrf=False)
    def get_model_data(self, model, **params):
        records = request.env[model].search([])
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
            records = request.env[model].search(filters)

        prev_page = None
        next_page = None
        total_page_number = 1
        current_page = 1

        if "page_size" in params:
            page_size = int(params["page_size"])
            count = len(records)
            total_page_number = math.ceil(count/page_size)

            if "page" in params:
                current_page = int(params["page"])
            else:
                current_page = 1  # Default page Number
            start = page_size*(current_page-1)
            stop = current_page*page_size
            records = records[start:stop]
            next_page = current_page+1 \
                        if 0 < current_page + 1 <= total_page_number \
                        else None
            prev_page = current_page-1 \
                        if 0 < current_page - 1 <= total_page_number \
                        else None

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
            "count": len(records),
            "prev": prev_page,
            "current": current_page,
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
        '/api/<string:model>/<int:rec_id>',
        auth='user', methods=['GET'], csrf=False)
    def get_model_rec(self, model, rec_id, **params):
        records = request.env[model].search([])
        if "query" in params:
            query = json.loads(params["query"])
        else:
            query = records.fields_get_keys()
        
        if "exclude" in params:
            exclude = json.loads(params["exclude"])
            for field in exclude:
                if field in query:
                    field_to_exclude = query.index(field)
                    query.pop(field_to_exclude)

        record = records.browse(rec_id).ensure_one()
        data = dictfier.dictfy(
            record,
            query,
            flat_obj=flat_obj,
            nested_flat_obj=nested_flat_obj,
            nested_iter_obj=nested_iter_obj
        )
        return http.Response(
            json.dumps(data),
            status=200,
            mimetype='application/json'
        )

    @http.route(
        '/api/<string:model>/', 
        type='json', auth="user", 
        methods=['POST'], website=True, csrf=False)
    def post_model_data(self, model, **post):
        try:
            data = post['data']
        except KeyError:
            _logger.exception(
                "'data' parameter is not found on POST request"
            )

        if "context" in post:
            context = post["context"]
            record = request.env[model].with_context(**context)\
                     .create(data)
        else:
            record = request.env[model].create(data)
        return record.id

    @http.route(
        '/api/<string:model>/<int:rec_id>/', 
        type='json', auth="user", 
        methods=['PUT'], website=True, csrf=False)
    def put_model_record(self, model, rec_id, **post):
        try:
            data = post['data']
        except KeyError:
            _logger.exception(
                "'data' parameter is not found on PUT request"
            )

        if "context" in post:
            rec = request.env[model].with_context(**post["context"])\
                  .browse(rec_id).ensure_one()
        else:
            rec = request.env[model].browse(rec_id).ensure_one()

        for field in data:
            if isinstance(data[field], dict):
                operations = []
                for operation in data[field]:
                    if operation == "push":
                        operations.extend(
                            (4, rec_id, _) 
                            for rec_id 
                            in data[field].get("push")
                        )
                    elif operation == "pop":
                        operations.extend(
                            (3, rec_id, _) 
                            for rec_id 
                            in data[field].get("pop")
                        )
                    elif operation == "delete":
                        operations.extend(
                            (2, rec_id, _) 
                            for rec_id 
                            in data[field].get("delete")
                        )
                    else:
                        data[field].pop(operation)  # Invalid operation

                data[field] = operations
            elif isinstance(data[field], list):
                data[field] = [(6, _, data[field])]  # Replace operation
            else:
                pass

        if rec.exists():
            return rec.write(data)
        else:
            return False

    @http.route(
        '/api/<string:model>/', 
        type='json', auth="user", 
        methods=['PUT'], website=True, csrf=False)
    def put_model_records(self, model, **post):
        try:
            data = post['data']
        except KeyError:
            _logger.exception(
                "'data' parameter is not found on PUT request"
            )

        filters = post["filter"]
        rec = request.env[model].search(filters)

        if "context" in post:
            rec = request.env[model].with_context(**post["context"])\
                  .search(filters)
        else:
            rec = request.env[model].search(filters)

        for field in data:
            if isinstance(data[field], dict):
                operations = []
                for operation in data[field]:
                    if operation == "push":
                        operations.extend(
                            (4, rec_id, _) 
                            for rec_id 
                            in data[field].get("push")
                        )
                    elif operation == "pop":
                        operations.extend(
                            (3, rec_id, _) 
                            for rec_id 
                            in data[field].get("pop")
                        )
                    elif operation == "delete":
                        operations.extend(
                            (2, rec_id, _) 
                            for rec_id in 
                            data[field].get("delete")
                        )
                    else:
                        pass  # Invalid operation

                data[field] = operations
            elif isinstance(data[field], list):
                data[field] = [(6, _, data[field])]  # Replace operation
            else:
                pass

        if rec.exists():
            return rec.write(data)
        else:
            return False

    @http.route(
        '/api/<string:model>/<int:rec_id>/', 
        type='http', auth="user", 
        methods=['DELETE'], website=True, csrf=False)
    def delete_model_record(self, model,  rec_id, **post):
        rec = request.env[model].browse(rec_id).ensure_one()
        if rec.exists():
            is_deleted = rec.unlink()
        else:
            is_deleted = False
        res = {
            "result": json.dumps(is_deleted)
        }
        return http.Response(
            json.dumps(res),
            status=200,
            mimetype='application/json'
        )

    @http.route(
        '/api/<string:model>/', 
        type='http', auth="user", 
        methods=['DELETE'], website=True, csrf=False)
    def delete_model_records(self, model, **post):
        filters = json.loads(post["filter"])
        rec = request.env[model].search(filters)
        if rec.exists():
            is_deleted = rec.unlink()
        else:
            is_deleted = False
        res = {
            "result": json.dumps(is_deleted)
        }
        return http.Response(
            json.dumps(res),
            status=200,
            mimetype='application/json'
        )


    @http.route(
        '/api/<string:model>/<int:rec_id>/<string:field>', 
        type='http', auth="user", 
        methods=['GET'], website=True, csrf=False)
    def get_binary_record(self, model,  rec_id, field, **post):
        rec = request.env[model].browse(rec_id).ensure_one()
        if rec.exists():
            src = getattr(rec, field).decode("utf-8")
        else:
            src = False
        return http.Response(
            src
        )

