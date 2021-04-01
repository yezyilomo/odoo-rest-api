# -*- coding: utf-8 -*-
import json
import logging
import math

import requests
from odoo import http, _
from odoo.http import request

from .exceptions import QueryFormatError
from .serializers import Serializer

_logger = logging.getLogger(__name__)


class OdooAPI(http.Controller):
    @http.route(
        '/auth/',
        type='json', auth='none', methods=["POST"], csrf=False)
    def authenticate(self, *args, **post):
        try:
            login = post["login"]
            password = post["password"]
            db = post["db"]
        except KeyError as e:
            return self.error_response(e, f"`{str(e)}` is required.")

        try:
            url_root = request.httprequest.url_root
            auth_url = f"{url_root}web/session/authenticate/"

            data = {
                "jsonrpc": "2.0",
                "params": {
                    "login": login,
                    "password": password,
                    "db": db
                }
            }

            res = requests.post(
                auth_url,
                data=json.dumps(data),
                headers={'Content-type': 'application/json'}
            )

            session_id = res.cookies["session_id"]
            user = json.loads(res.text)
            user["result"]["session_id"] = session_id
        except Exception as e:
            return self.error_response(e, "Invalid credentials.")
        return user["result"]

    @http.route(
        '/object/<string:model>/<string:function>',
        type='json', auth='user', methods=["POST"], csrf=False)
    def call_model_function(self, model, function, **post):
        args = post.get("args", [])
        kwargs = post.get("kwargs", {})
        model = request.env[model]
        result = getattr(model, function)(*args, **kwargs)
        return result

    @http.route(
        '/object/<string:model>/<int:rec_id>/<string:function>',
        type='json', auth='user', methods=["POST"], csrf=False)
    def call_obj_function(self, model, rec_id, function, **post):
        args = post.get("args", [])
        kwargs = post.get("kwargs", {})
        obj = request.env[model].browse(rec_id).ensure_one()
        result = getattr(obj, function)(*args, **kwargs)
        return result

    @http.route(
        '/report/<string:model>/<int:rec_id>',
        type='json', auth='user', methods=["POST"], csrf=False)
    def call_render_qweb_pdf(self, model, rec_id, **post):
        result = getattr('ir.actions.report', 'render_qweb_pdf')(post.get('res_ids'), post.get('data'))
        return result

    @http.route(
        '/api/<string:model>',
        type='http', auth='user', methods=['GET'], csrf=False)
    def get_model_data(self, model, **params):
        try:
            records = request.env[model].search([])
        except KeyError as e:
            msg = f"The model `{model}` does not exist."
            return self.error_response(e, msg)

        query = params.get("query", "{*}")
        orders = json.loads(params["order"]) if "order" in params else ""

        if "filter" in params:
            filters = json.loads(params["filter"])
            records = request.env[model].search(filters, order=orders)

        prev_page = None
        next_page = None
        total_page_number = 1
        current_page = 1

        if "page_size" in params:
            page_size = int(params["page_size"])
            count = len(records)
            total_page_number = math.ceil(count / page_size)

            current_page = int(params["page"]) if "page" in params else 1
            start = page_size * (current_page - 1)
            stop = current_page * page_size
            records = records[start:stop]
            next_page = current_page + 1 \
                if 0 < current_page + 1 <= total_page_number else None
            prev_page = current_page - 1 \
                if 0 < current_page - 1 <= total_page_number else None

        if "limit" in params:
            limit = int(params["limit"])
            records = records[0:limit]

        try:
            serializer = Serializer(records, query, many=True)
            data = serializer.data
        except (SyntaxError, QueryFormatError) as e:
            return self.error_response(e)

        res = {
            "count": len(records),
            "prev": prev_page,
            "current": current_page,
            "next": next_page,
            "total_pages": total_page_number,
            "result": data
        }
        return self.response(res)

    @http.route(
        '/api/<string:model>/<int:rec_id>',
        type='http', auth='user', methods=['GET'], csrf=False)
    def get_model_rec(self, model, rec_id, **params):
        try:
            records = request.env[model].search([])
        except KeyError as e:
            msg = f"The model `{model}` does not exist."
            return self.error_response(e, msg)

        # TODO: Handle the error raised by `ensure_one`
        record = records.browse(rec_id).ensure_one()

        try:
            query = params.get("query", "{*}")
            serializer = Serializer(record, query)
        except (SyntaxError, QueryFormatError) as e:
            return self.error_response(e)

        return self.response(serializer.data)

    @http.route(
        '/api/<string:model>/',
        type='json', auth="user", methods=['POST'], csrf=False)
    def post_model_data(self, model, **post):
        try:
            data = post['data']
        except KeyError as e:
            msg = "`data` parameter is not found on POST request body"
            return self.error_response(e, msg)

        try:
            model_to_post = request.env[model]
        except KeyError as e:
            msg = f"The model `{model}` does not exist."
            return self.error_response(e, msg)

        # TODO: Handle data validation

        if "context" in post:
            context = post["context"]
            record = model_to_post.with_context(**context).create(data)
        else:
            record = model_to_post.create(data)
        return record.id

    # This is for single record update
    @http.route(
        '/api/<string:model>/<int:rec_id>/',
        type='json', auth="user", methods=['PUT'], csrf=False)
    def put_model_record(self, model, rec_id, **post):
        try:
            data = post['data']
        except KeyError as e:
            msg = "`data` parameter is not found on PUT request body"
            return self.error_response(e, msg)

        try:
            model_to_put = request.env[model]
        except KeyError as e:
            msg = f"The model `{model}` does not exist."
            return self.error_response(e, msg)

        if "context" in post:
            # TODO: Handle error raised by `ensure_one`
            rec = model_to_put.with_context(**post["context"]).browse(rec_id).ensure_one()
        else:
            rec = model_to_put.browse(rec_id).ensure_one()

        # TODO: Handle data validation
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

        try:
            return rec.write(data)
        except Exception as e:
            # TODO: Return error message(e.msg) on a response
            return False

    # This is for bulk update
    @http.route(
        '/api/<string:model>/',
        type='json', auth="user", methods=['PUT'], csrf=False)
    def put_model_records(self, model, **post):
        try:
            data = post['data']
        except KeyError as e:
            msg = "`data` parameter is not found on PUT request body"
            return self.error_response(e, msg)

        try:
            model_to_put = request.env[model]
        except KeyError as e:
            msg = f"The model `{model}` does not exist."
            return self.error_response(e, msg)

        # TODO: Handle errors on filter
        filters = post["filter"]

        if "context" in post:
            recs = model_to_put.with_context(**post["context"]).search(filters)
        else:
            recs = model_to_put.search(filters)

        # TODO: Handle data validation
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

        if recs.exists():
            try:
                return recs.write(data)
            except Exception as e:
                # TODO: Return error message(e.msg) on a response
                return False
        else:
            # No records to update
            return True

    # This is for deleting one record
    @http.route(
        '/api/<string:model>/<int:rec_id>/',
        type='http', auth="user", methods=['DELETE'], csrf=False)
    def delete_model_record(self, model, rec_id, **post):
        try:
            model_to_del_rec = request.env[model]
        except KeyError as e:
            msg = f"The model `{model}` does not exist."
            return self.error_response(e, msg)

        # TODO: Handle error raised by `ensure_one`
        rec = model_to_del_rec.browse(rec_id).ensure_one()

        try:
            is_deleted = rec.unlink()
            res = {
                "result": is_deleted
            }
            return self.response(res)
        except Exception as e:
            return self.error_response(e)

    # This is for bulk deletion
    @http.route(
        '/api/<string:model>/',
        type='http', auth="user", methods=['DELETE'], csrf=False)
    def delete_model_records(self, model, **post):
        try:
            model_to_del_rec = request.env[model]
        except KeyError as e:
            msg = f"The model `{model}` does not exist."
            return self.error_response(e, msg)

        # TODO: Handle error raised by `filters`
        filters = json.loads(post["filter"])
        recs = model_to_del_rec.search(filters)

        try:
            is_deleted = recs.unlink()
            res = {
                "result": is_deleted
            }
            return self.response(res)
        except Exception as e:
            return self.error_response(e)

    @http.route(
        '/api/<string:model>/<int:rec_id>/<string:field>',
        type='http', auth="user", methods=['GET'], csrf=False)
    def get_binary_record(self, model, rec_id, field, **post):
        try:
            request.env[model]
        except KeyError as e:
            msg = f"The model `{model}` does not exist."
            return self.error_response(e, msg)

        try:
            rec = request.env[model].browse(rec_id).ensure_one()
            src = getattr(rec, field).decode("utf-8") if rec.exists() else False
            return http.Response(src)
        except Exception as e:
            return self.error_response(e)

    def error_response(self, e: Exception, msg: str = None):
        res = {
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": 200,
                "message": msg or str(e),
                "data": {
                    "name": str(e),
                    "debug": "",
                    "message": msg,
                    "arguments": list(e.args),
                    "exception_type": type(e).__name__
                }
            }
        }
        return self.response(res)

    @staticmethod
    def response(res: dict):
        return http.Response(
            json.dumps(res),
            status=200,
            mimetype='application/json'
        )
