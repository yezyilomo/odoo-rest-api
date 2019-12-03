# -*- coding: utf-8 -*-
import json
import math
import logging
import requests
import datetime
from itertools import chain

from odoo import http, _
from odoo.http import request

from .parser import Parser


_logger = logging.getLogger(__name__)


class Serializer(object):
    def __init__(self, record, query="{*}", many=False):
        self.many = many
        self._record = record
        self._raw_query = query
        super().__init__()

    def get_parsed_restql_query(self):
        parser = Parser(self._raw_query)
        try:
            parsed_restql_query = parser.get_parsed()
            return parsed_restql_query
        except SyntaxError as e:
            msg = (
                "QueryFormatError: " + 
                e.msg + " on " + 
                e.text
            )
            raise SyntaxError(msg) from None

    @property
    def data(self):
        parsed_restql_query = self.get_parsed_restql_query()
        if self.many:
            return [
                self.serialize(rec, parsed_restql_query)
                for rec
                in self._record
            ]
        return self.serialize(self._record, parsed_restql_query)

    @classmethod
    def build_flat_field(cls, rec, field_name):
        all_fields = rec.fields_get_keys()
        if field_name not in all_fields:
            msg = "'%s' field is not found" % field_name
            raise LookupError(msg)
        field_type = rec.fields_get(field_name).get(field_name).get('type')
        if field_type in ['one2many', 'many2many']:
            return {
                field_name: [record.id for record in rec[field_name]]
            }
        elif field_type in ['many2one']:
            return {field_name: rec[field_name].id}
        elif field_type == 'datetime' and rec[field_name]:
            return {
                field_name: rec[field_name].strftime("%Y-%m-%d-%H-%M")
            }
        elif field_type == 'date' and rec[field_name]:
            return {
                field_name: rec[field_name].strftime("%Y-%m-%d")
            }
        elif field_type == 'time' and rec[field_name]:
            return {
                field_name: rec[field_name].strftime("%H-%M-%S")
            }
        elif field_type == "binary" and rec[field_name]:
            return {field_name: rec[field_name].decode("utf-8")}
        else:
            return {field_name: rec[field_name]}

    @classmethod
    def build_nested_field(cls, rec, field_name, nested_parsed_query):
        all_fields = rec.fields_get_keys()
        if field_name not in all_fields:
            msg = "'%s' field is not found" % field_name
            raise LookupError(msg)
        field_type = rec.fields_get(field_name).get(field_name).get('type')
        if field_type in ['one2many', 'many2many']:
            return {
                field_name: [
                    cls.serialize(record, nested_parsed_query) 
                    for record 
                    in rec[field_name]
                ]
            }
        elif field_type in ['many2one']:
            return {
                field_name: cls.serialize(rec[field_name], nested_parsed_query)
            }
        else:
            # Not a neste field
            msg = "'%s' is not a nested field" % field_name
            raise ValueError(msg)

    @classmethod
    def serialize(cls, rec, parsed_query):
        data = {}
    
        # NOTE: self.parsed_restql_query["include"] not being empty 
        # is not a guarantee that the exclude operator(-) has not been 
        # used because the same self.parsed_restql_query["include"]
        # is used to store nested fields when the exclude operator(-) is used
        if parsed_query["exclude"]:
            # Exclude fields from a query
            all_fields = rec.fields_get_keys()
            for field in parsed_query["include"]:
                if field == "*":
                    continue
                for nested_field, nested_parsed_query in field.items():
                    built_nested_field = cls.build_nested_field(
                        rec, 
                        nested_field, 
                        nested_parsed_query
                    )
                    data.update(built_nested_field)
    
            flat_fields= set(all_fields).symmetric_difference(set(parsed_query['exclude']))
            for field in flat_fields:
                flat_field = cls.build_flat_field(rec, field)
                data.update(flat_field)
    
        elif parsed_query["include"]:
            # Here we are sure that self.parsed_restql_query["exclude"]
            # is empty which means the exclude operator(-) is not used,
            # so self.parsed_restql_query["include"] contains only fields
            # to include
            all_fields = rec.fields_get_keys()
            if "*" in parsed_query['include']:
                # Include all fields
                parsed_query['include'] = filter(
                    lambda item: item != "*", 
                    parsed_query['include']
                )
                fields = chain(parsed_query['include'], all_fields)
                parsed_query['include'] = reversed(list(fields))

            for field in parsed_query["include"]:
                if isinstance(field, dict):
                    for nested_field, nested_parsed_query in field.items():
                        built_nested_field = cls.build_nested_field(
                            rec, 
                            nested_field, 
                            nested_parsed_query
                        )
                        data.update(built_nested_field)
                else:
                    flat_field = cls.build_flat_field(rec, field)
                    data.update(flat_field)
        else:
            # The query is empty i.e query={}
            # return nothing
            return {}
        return data


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
            query = params["query"]
        else:
            query = "{*}"
        
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

        serializer = Serializer(records, query ,many=True)

        res = {
            "count": len(records),
            "prev": prev_page,
            "current": current_page,
            "next": next_page,
            "total_pages": total_page_number,
            "result": serializer.data
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
            query = params["query"]
        else:
            query = "{*}"

        record = records.browse(rec_id).ensure_one()
        serializer = Serializer(record, query)
        return http.Response(
            json.dumps(serializer.data),
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

