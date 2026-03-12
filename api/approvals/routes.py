"""Approval Types and Requests routes"""
from flask import Blueprint, request, jsonify
from utils.odoo_helper import execute_odoo_kw, check_odoo_error
from utils.auth_helper import check_permission
from utils.config import PASSWORD

approvals_bp = Blueprint("approvals", __name__)


# -------- Approval Types (multi.approval.type) --------

@approvals_bp.route("/approval/types", methods=["GET"])
@check_permission("multi.approval.type", "read", use_cache=False)
def get_approval_types(current_user):
    """Lấy danh sách Approval Types"""
    try:
        uid = current_user["uid"]
        user_password = current_user.get("password", PASSWORD)

        limit = request.args.get("limit", 10, type=int)
        offset = request.args.get("offset", 0, type=int)
        search = request.args.get("search")
        fields = request.args.get(
            "fields",
            "id,name,approval_minimum,document_opt,contact_opt,date_opt,period_opt,"
            "item_opt,multi_items_opt,quantity_opt,amount_opt,reference_opt,"
            "payment_opt,location_opt,submitted_nb,activity_notification",
        )
        fields_list = [f.strip() for f in fields.split(",") if f.strip()]

        domain = []
        if search:
            domain = [["name", "ilike", search]]

        res = execute_odoo_kw(
            uid,
            user_password,
            "multi.approval.type",
            "search_read",
            [domain],
            {"fields": fields_list, "limit": limit, "offset": offset},
        )

        has_error, error_message, status_code = check_odoo_error(res)
        if has_error:
            if status_code == 403:
                return (
                    jsonify(
                        {
                            "error": "Bạn không có quyền truy cập dữ liệu này",
                            "message": "Quyền đã bị khóa trên Odoo.",
                            "odoo_error": error_message,
                        }
                    ),
                    403,
                )
            return (
                jsonify(
                    {
                        "error": "Lỗi khi truy vấn dữ liệu từ Odoo",
                        "odoo_error": error_message,
                    }
                ),
                status_code,
            )

        result = res.get("result", [])
        return (
            jsonify(
                {
                    "data": result,
                    "count": len(result),
                    "user": current_user["username"],
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"error": f"Lỗi server: {str(e)}"}), 500


@approvals_bp.route("/approval/types/<int:type_id>", methods=["GET"])
@check_permission("multi.approval.type", "read", use_cache=False)
def get_approval_type(current_user, type_id):
    """Lấy thông tin 1 Approval Type"""
    try:
        uid = current_user["uid"]
        user_password = current_user.get("password", PASSWORD)

        res = execute_odoo_kw(
            uid,
            user_password,
            "multi.approval.type",
            "read",
            [type_id],
            {
                "fields": [
                    "id",
                    "name",
                    "approval_minimum",
                    "document_opt",
                    "contact_opt",
                    "date_opt",
                    "period_opt",
                    "item_opt",
                    "multi_items_opt",
                    "quantity_opt",
                    "amount_opt",
                    "reference_opt",
                    "payment_opt",
                    "location_opt",
                    "submitted_nb",
                    "line_ids",
                ]
            },
        )

        has_error, error_message, status_code = check_odoo_error(res)
        if has_error:
            if status_code == 403:
                return (
                    jsonify(
                        {
                            "error": "Bạn không có quyền truy cập dữ liệu này",
                            "odoo_error": error_message,
                        }
                    ),
                    403,
                )
            return (
                jsonify(
                    {
                        "error": "Lỗi khi truy vấn dữ liệu từ Odoo",
                        "odoo_error": error_message,
                    }
                ),
                status_code,
            )

        result = res.get("result", [])
        if not result:
            return jsonify({"error": "Approval Type không tồn tại"}), 404

        return (
            jsonify({"data": result[0], "user": current_user["username"]}),
            200,
        )
    except Exception as e:
        return jsonify({"error": f"Lỗi server: {str(e)}"}), 500


@approvals_bp.route("/approval/types", methods=["POST"])
@check_permission("multi.approval.type", "create", use_cache=False)
def create_approval_type(current_user):
    """Tạo Approval Type mới"""
    try:
        uid = current_user["uid"]
        user_password = current_user.get("password", PASSWORD)
        data = request.get_json()

        if not data:
            return jsonify({"error": "Vui lòng cung cấp dữ liệu Approval Type"}), 400

        if not data.get("name"):
            return jsonify({"error": "Tên Approval Type là bắt buộc"}), 400

        res = execute_odoo_kw(
            uid,
            user_password,
            "multi.approval.type",
            "create",
            [data],
            {},
        )

        has_error, error_message, status_code = check_odoo_error(res)
        if has_error:
            if status_code == 403:
                return (
                    jsonify(
                        {
                            "error": "Bạn không có quyền tạo Approval Type",
                            "odoo_error": error_message,
                        }
                    ),
                    403,
                )
            return (
                jsonify(
                    {
                        "error": "Lỗi khi tạo Approval Type",
                        "odoo_error": error_message,
                    }
                ),
                status_code,
            )

        type_id = res.get("result")
        return (
            jsonify(
                {
                    "message": "Tạo Approval Type thành công",
                    "id": type_id,
                    "user": current_user["username"],
                }
            ),
            201,
        )
    except Exception as e:
        return jsonify({"error": f"Lỗi server: {str(e)}"}), 500


@approvals_bp.route("/approval/types/<int:type_id>", methods=["PUT"])
@check_permission("multi.approval.type", "write", use_cache=False)
def update_approval_type(current_user, type_id):
    """Cập nhật Approval Type"""
    try:
        uid = current_user["uid"]
        user_password = current_user.get("password", PASSWORD)
        data = request.get_json()

        if not data:
            return jsonify({"error": "Vui lòng cung cấp dữ liệu cập nhật"}), 400

        res = execute_odoo_kw(
            uid,
            user_password,
            "multi.approval.type",
            "write",
            [[type_id], data],
            {},
        )

        has_error, error_message, status_code = check_odoo_error(res)
        if has_error:
            if status_code == 403:
                return (
                    jsonify(
                        {
                            "error": "Bạn không có quyền cập nhật Approval Type",
                            "odoo_error": error_message,
                        }
                    ),
                    403,
                )
            return (
                jsonify(
                    {
                        "error": "Lỗi khi cập nhật Approval Type",
                        "odoo_error": error_message,
                    }
                ),
                status_code,
            )

        return (
            jsonify(
                {
                    "message": "Cập nhật Approval Type thành công",
                    "id": type_id,
                    "user": current_user["username"],
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"error": f"Lỗi server: {str(e)}"}), 500


@approvals_bp.route("/approval/types/<int:type_id>", methods=["DELETE"])
@check_permission("multi.approval.type", "unlink", use_cache=False)
def delete_approval_type(current_user, type_id):
    """Xóa Approval Type"""
    try:
        uid = current_user["uid"]
        user_password = current_user.get("password", PASSWORD)

        res = execute_odoo_kw(
            uid,
            user_password,
            "multi.approval.type",
            "unlink",
            [[type_id]],
            {},
        )

        has_error, error_message, status_code = check_odoo_error(res)
        if has_error:
            if status_code == 403:
                return (
                    jsonify(
                        {
                            "error": "Bạn không có quyền xóa Approval Type",
                            "odoo_error": error_message,
                        }
                    ),
                    403,
                )
            return (
                jsonify(
                    {
                        "error": "Lỗi khi xóa Approval Type",
                        "odoo_error": error_message,
                    }
                ),
                status_code,
            )

        return (
            jsonify(
                {
                    "message": "Xóa Approval Type thành công",
                    "id": type_id,
                    "user": current_user["username"],
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"error": f"Lỗi server: {str(e)}"}), 500


# -------- Approval Requests (multi.approval) --------


@approvals_bp.route("/approval/requests", methods=["GET"])
@check_permission("multi.approval", "read", use_cache=False)
def get_approval_requests(current_user):
    """Lấy danh sách Approval Requests"""
    try:
        uid = current_user["uid"]
        user_password = current_user.get("password", PASSWORD)

        limit = request.args.get("limit", 10, type=int)
        offset = request.args.get("offset", 0, type=int)
        status = request.args.get("status")
        type_id = request.args.get("type_id", type=int)
        to_review = request.args.get("to_review", type=str)
        fields = request.args.get(
            "fields",
            "id,name,user_id,type_id,state,amount,reference,request_date,priority",
        )
        fields_list = [f.strip() for f in fields.split(",") if f.strip()]

        domain = []
        if status:
            domain.append(["state", "=", status])
        if type_id:
            domain.append(["type_id", "=", type_id])
        if to_review and to_review.lower() in ("1", "true", "yes"):
            domain.append(["pic_id", "=", uid])

        res = execute_odoo_kw(
            uid,
            user_password,
            "multi.approval",
            "search_read",
            [domain],
            {"fields": fields_list, "limit": limit, "offset": offset},
        )

        has_error, error_message, status_code = check_odoo_error(res)
        if has_error:
            if status_code == 403:
                return (
                    jsonify(
                        {
                            "error": "Bạn không có quyền truy cập dữ liệu này",
                            "message": "Quyền đã bị khóa trên Odoo.",
                            "odoo_error": error_message,
                        }
                    ),
                    403,
                )
            return (
                jsonify(
                    {
                        "error": "Lỗi khi truy vấn dữ liệu từ Odoo",
                        "odoo_error": error_message,
                    }
                ),
                status_code,
            )

        result = res.get("result", [])
        return (
            jsonify(
                {
                    "data": result,
                    "count": len(result),
                    "user": current_user["username"],
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"error": f"Lỗi server: {str(e)}"}), 500


@approvals_bp.route("/approval/requests/to-review", methods=["GET"])
@check_permission("multi.approval", "read", use_cache=False)
def get_requests_to_review(current_user):
    """Lấy danh sách phiếu cần user hiện tại duyệt"""
    try:
        uid = current_user["uid"]
        user_password = current_user.get("password", PASSWORD)

        limit = request.args.get("limit", 10, type=int)
        offset = request.args.get("offset", 0, type=int)
        fields = request.args.get(
            "fields",
            "id,name,user_id,type_id,state,amount,reference,request_date,priority",
        )
        fields_list = [f.strip() for f in fields.split(",") if f.strip()]

        domain = [
            ["pic_id", "=", uid],
            ["state", "=", "Submitted"],
        ]

        res = execute_odoo_kw(
            uid,
            user_password,
            "multi.approval",
            "search_read",
            [domain],
            {"fields": fields_list, "limit": limit, "offset": offset},
        )

        has_error, error_message, status_code = check_odoo_error(res)
        if has_error:
            if status_code == 403:
                return (
                    jsonify(
                        {
                            "error": "Bạn không có quyền truy cập dữ liệu này",
                            "message": "Quyền đã bị khóa trên Odoo.",
                            "odoo_error": error_message,
                        }
                    ),
                    403,
                )
            return (
                jsonify(
                    {
                        "error": "Lỗi khi truy vấn dữ liệu từ Odoo",
                        "odoo_error": error_message,
                    }
                ),
                status_code,
            )

        result = res.get("result", [])
        return (
            jsonify(
                {
                    "data": result,
                    "count": len(result),
                    "user": current_user["username"],
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"error": f"Lỗi server: {str(e)}"}), 500


@approvals_bp.route("/approval/requests/<int:request_id>", methods=["GET"])
@check_permission("multi.approval", "read", use_cache=False)
def get_approval_request(current_user, request_id):
    """Lấy chi tiết 1 Approval Request"""
    try:
        uid = current_user["uid"]
        user_password = current_user.get("password", PASSWORD)

        res = execute_odoo_kw(
            uid,
            user_password,
            "multi.approval",
            "read",
            [request_id],
            {
                "fields": [
                    "id",
                    "name",
                    "user_id",
                    "type_id",
                    "state",
                    "amount",
                    "reference",
                    "request_date",
                    "reason",
                    "line_ids",
                    "activity_ids",
                ]
            },
        )

        has_error, error_message, status_code = check_odoo_error(res)
        if has_error:
            if status_code == 403:
                return (
                    jsonify(
                        {
                            "error": "Bạn không có quyền truy cập dữ liệu này",
                            "odoo_error": error_message,
                        }
                    ),
                    403,
                )
            return (
                jsonify(
                    {
                        "error": "Lỗi khi truy vấn dữ liệu từ Odoo",
                        "odoo_error": error_message,
                    }
                ),
                status_code,
            )

        result = res.get("result", [])
        if not result:
            return jsonify({"error": "Approval Request không tồn tại"}), 404

        return (
            jsonify({"data": result[0], "user": current_user["username"]}),
            200,
        )
    except Exception as e:
        return jsonify({"error": f"Lỗi server: {str(e)}"}), 500


@approvals_bp.route("/approval/requests", methods=["POST"])
@check_permission("multi.approval", "create", use_cache=False)
def create_approval_request(current_user):
    """Tạo Approval Request mới"""
    try:
        uid = current_user["uid"]
        user_password = current_user.get("password", PASSWORD)
        data = request.get_json()

        if not data:
            return jsonify({"error": "Vui lòng cung cấp dữ liệu Approval Request"}), 400

        if not data.get("type_id") or not data.get("name"):
            return jsonify({"error": "type_id và name là bắt buộc"}), 400

        res = execute_odoo_kw(
            uid,
            user_password,
            "multi.approval",
            "create",
            [data],
            {},
        )

        has_error, error_message, status_code = check_odoo_error(res)
        if has_error:
            if status_code == 403:
                return (
                    jsonify(
                        {
                            "error": "Bạn không có quyền tạo Approval Request",
                            "odoo_error": error_message,
                        }
                    ),
                    403,
                )
            return (
                jsonify(
                    {
                        "error": "Lỗi khi tạo Approval Request",
                        "odoo_error": error_message,
                    }
                ),
                status_code,
            )

        request_id = res.get("result")
        return (
            jsonify(
                {
                    "message": "Tạo Approval Request thành công",
                    "id": request_id,
                    "user": current_user["username"],
                }
            ),
            201,
        )
    except Exception as e:
        return jsonify({"error": f"Lỗi server: {str(e)}"}), 500


@approvals_bp.route("/approval/requests/<int:request_id>", methods=["PUT"])
@check_permission("multi.approval", "write", use_cache=False)
def update_approval_request(current_user, request_id):
    """Cập nhật Approval Request (khi chưa duyệt xong)"""
    try:
        uid = current_user["uid"]
        user_password = current_user.get("password", PASSWORD)
        data = request.get_json()

        if not data:
            return jsonify({"error": "Vui lòng cung cấp dữ liệu cập nhật"}), 400

        res = execute_odoo_kw(
            uid,
            user_password,
            "multi.approval",
            "write",
            [[request_id], data],
            {},
        )

        has_error, error_message, status_code = check_odoo_error(res)
        if has_error:
            if status_code == 403:
                return (
                    jsonify(
                        {
                            "error": "Bạn không có quyền cập nhật Approval Request",
                            "odoo_error": error_message,
                        }
                    ),
                    403,
                )
            return (
                jsonify(
                    {
                        "error": "Lỗi khi cập nhật Approval Request",
                        "odoo_error": error_message,
                    }
                ),
                status_code,
            )

        return (
            jsonify(
                {
                    "message": "Cập nhật Approval Request thành công",
                    "id": request_id,
                    "user": current_user["username"],
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"error": f"Lỗi server: {str(e)}"}), 500


@approvals_bp.route("/approval/requests/<int:request_id>/cancel", methods=["POST"])
@check_permission("multi.approval", "write", use_cache=False)
def cancel_approval_request(current_user, request_id):
    """Hủy Approval Request"""
    try:
        uid = current_user["uid"]
        user_password = current_user.get("password", PASSWORD)

        res = execute_odoo_kw(
            uid,
            user_password,
            "multi.approval",
            "action_cancel",
            [[request_id]],
            {},
        )

        has_error, error_message, status_code = check_odoo_error(res)
        if has_error:
            if status_code == 403:
                return (
                    jsonify(
                        {
                            "error": "Bạn không có quyền hủy Approval Request",
                            "odoo_error": error_message,
                        }
                    ),
                    403,
                )
            return (
                jsonify(
                    {
                        "error": "Lỗi khi hủy Approval Request",
                        "odoo_error": error_message,
                    }
                ),
                status_code,
            )

        return (
            jsonify(
                {
                    "message": "Hủy Approval Request thành công",
                    "id": request_id,
                    "user": current_user["username"],
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"error": f"Lỗi server: {str(e)}"}), 500


@approvals_bp.route("/approval/requests/<int:request_id>/approve", methods=["POST"])
@check_permission("multi.approval", "write", use_cache=False)
def approve_request(current_user, request_id):
    """Manager approve Approval Request"""
    try:
        uid = current_user["uid"]
        user_password = current_user.get("password", PASSWORD)

        res = execute_odoo_kw(
            uid,
            user_password,
            "multi.approval",
            "action_approve",
            [[request_id]],
            {},
        )

        has_error, error_message, status_code = check_odoo_error(res)
        if has_error:
            if status_code == 403:
                return (
                    jsonify(
                        {
                            "error": "Bạn không có quyền approve Approval Request",
                            "odoo_error": error_message,
                        }
                    ),
                    403,
                )
            return (
                jsonify(
                    {
                        "error": "Lỗi khi approve Approval Request",
                        "odoo_error": error_message,
                    }
                ),
                status_code,
            )

        return (
            jsonify(
                {
                    "message": "Approve Approval Request thành công",
                    "id": request_id,
                    "user": current_user["username"],
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"error": f"Lỗi server: {str(e)}"}), 500


@approvals_bp.route("/approval/requests/<int:request_id>/reject", methods=["POST"])
@check_permission("multi.approval", "write", use_cache=False)
def reject_request(current_user, request_id):
    """Manager reject Approval Request"""
    try:
        uid = current_user["uid"]
        user_password = current_user.get("password", PASSWORD)

        res = execute_odoo_kw(
            uid,
            user_password,
            "multi.approval",
            "action_refuse",
            [[request_id]],
            {},
        )

        has_error, error_message, status_code = check_odoo_error(res)
        if has_error:
            if status_code == 403:
                return (
                    jsonify(
                        {
                            "error": "Bạn không có quyền reject Approval Request",
                            "odoo_error": error_message,
                        }
                    ),
                    403,
                )
            return (
                jsonify(
                    {
                        "error": "Lỗi khi reject Approval Request",
                        "odoo_error": error_message,
                    }
                ),
                status_code,
            )

        return (
            jsonify(
                {
                    "message": "Reject Approval Request thành công",
                    "id": request_id,
                    "user": current_user["username"],
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"error": f'Lỗi server: {str(e)}'}), 500

