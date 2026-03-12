# API Examples - Curl Commands

Base URL: `http://localhost:5001`

## 1. Health Check

### Kiểm tra server
```bash
curl -X GET http://localhost:5001/health
```

## 2. Authentication APIs

### 2.1. Login - Đăng nhập để lấy token
```bash
curl -X POST http://localhost:5001/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "userTest@gmail.com",
    "password": "password"
  }'
```

**Response:**
```json
{
  "message": "Đăng nhập thành công",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "username": "userTest@gmail.com",
    "uid": 7,
    "groups": [],
    "is_superuser": false
  }
}
```

**Lưu token để dùng cho các API sau:**
```bash
# Lưu token vào biến
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 2.2. Get Current User - Lấy thông tin user hiện tại
```bash
curl -X GET http://localhost:5001/me \
  -H "Authorization: Bearer $TOKEN"
```

**Hoặc:**
```bash
curl -X GET http://localhost:5001/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## 3. Employees APIs

### 3.1. Get All Employees - Lấy danh sách employees
```bash
curl -X GET "http://localhost:5001/api/employees" \
  -H "Authorization: Bearer $TOKEN"
```

**Với query parameters:**
```bash
# Lấy 10 employees đầu tiên
curl -X GET "http://localhost:5001/api/employees?limit=10&offset=0" \
  -H "Authorization: Bearer $TOKEN"

# Lấy với các fields cụ thể
curl -X GET "http://localhost:5001/api/employees?limit=10&offset=0&fields=id,name,work_email,work_phone" \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "name": "John Doe",
      "work_email": "john@example.com",
      "work_phone": "0123456789"
    }
  ],
  "count": 1,
  "user": "userTest@gmail.com"
}
```

### 3.2. Get Employee by ID - Lấy thông tin 1 employee
```bash
curl -X GET http://localhost:5001/api/employees/1 \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "data": {
    "id": 1,
    "name": "John Doe",
    "work_email": "john@example.com",
    "work_phone": "0123456789",
    "department_id": [1, "IT Department"],
    "job_id": [1, "Developer"]
  },
  "user": "userTest@gmail.com"
}
```

### 3.3. Create Employee - Tạo employee mới
```bash
curl -X POST http://localhost:5001/api/employees \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Smith",
    "work_email": "jane@example.com",
    "work_phone": "0987654321",
    "department_id": 1,
    "job_id": 1
  }'
```

**Response:**
```json
{
  "message": "Tạo employee thành công",
  "id": 2,
  "user": "userTest@gmail.com"
}
```

### 3.4. Update Employee - Cập nhật employee
```bash
curl -X PUT http://localhost:5001/api/employees/2 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Smith Updated",
    "work_email": "jane.updated@example.com",
    "work_phone": "0999999999"
  }'
```

**Response:**
```json
{
  "message": "Cập nhật employee thành công",
  "id": 2,
  "user": "userTest@gmail.com"
}
```

### 3.5. Delete Employee - Xóa employee
```bash
curl -X DELETE http://localhost:5001/api/employees/2 \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "message": "Xóa employee thành công",
  "id": 2,
  "user": "userTest@gmail.com"
}
```

## 4. Complete Workflow Example

### Bước 1: Login và lưu token
```bash
# Login
RESPONSE=$(curl -s -X POST http://localhost:5001/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "userTest@gmail.com",
    "password": "password"
  }')

# Lấy token từ response
TOKEN=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['token'])")

echo "Token: $TOKEN"
```

### Bước 2: Lấy thông tin user hiện tại
```bash
curl -X GET http://localhost:5001/me \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### Bước 3: Lấy danh sách employees
```bash
curl -X GET "http://localhost:5001/api/employees?limit=10" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### Bước 4: Tạo employee mới
```bash
curl -X POST http://localhost:5001/api/employees \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Employee",
    "work_email": "new@example.com",
    "work_phone": "0123456789"
  }' | python3 -m json.tool
```

### Bước 5: Cập nhật employee
```bash
curl -X PUT http://localhost:5001/api/employees/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Employee Name"
  }' | python3 -m json.tool
```

### Bước 6: Xóa employee
```bash
curl -X DELETE http://localhost:5001/api/employees/1 \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

## 4. Contacts APIs (res.partner)

### 4.1. Get All Contacts - Lấy danh sách contacts
```bash
curl -X GET "http://localhost:5001/api/contacts" \
  -H "Authorization: Bearer $TOKEN"
```

**Với query parameters:**
```bash
# Lấy 10 contacts đầu tiên
curl -X GET "http://localhost:5001/api/contacts?limit=10&offset=0" \
  -H "Authorization: Bearer $TOKEN"

# Lấy với các fields cụ thể
curl -X GET "http://localhost:5001/api/contacts?limit=10&offset=0&fields=id,name,email,phone" \
  -H "Authorization: Bearer $TOKEN"

# Tìm kiếm contacts
curl -X GET "http://localhost:5001/api/contacts?search=john&limit=10" \
  -H "Authorization: Bearer $TOKEN"

# Lấy chỉ companies
curl -X GET "http://localhost:5001/api/contacts?is_company=true&limit=10" \
  -H "Authorization: Bearer $TOKEN"

# Lấy chỉ customers
curl -X GET "http://localhost:5001/api/contacts?customer=true&limit=10" \
  -H "Authorization: Bearer $TOKEN"

# Lấy chỉ suppliers
curl -X GET "http://localhost:5001/api/contacts?supplier=true&limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "0123456789",
      "street": "123 Main St",
      "city": "Ho Chi Minh",
      "country_id": [84, "Vietnam"]
    }
  ],
  "count": 1,
  "user": "userTest@gmail.com"
}
```

### 4.2. Get Contact by ID - Lấy thông tin 1 contact
```bash
curl -X GET http://localhost:5001/api/contacts/1 \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "data": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "0123456789",
    "street": "123 Main St",
    "street2": "Building A",
    "city": "Ho Chi Minh",
    "state_id": [1, "Ho Chi Minh City"],
    "country_id": [84, "Vietnam"],
    "zip": "70000",
    "is_company": false,
    "customer_rank": 1,
    "supplier_rank": 0,
    "category_id": [[1, "Category 1"]],
    "comment": "Notes about contact"
  },
  "user": "userTest@gmail.com"
}
```

### 4.3. Create Contact - Tạo contact mới
```bash
# Tạo contact cá nhân
curl -X POST http://localhost:5001/api/contacts \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Smith",
    "email": "jane@example.com",
    "phone": "0987654321",
    "street": "456 Park Ave",
    "city": "Hanoi",
    "country_id": 84,
    "is_company": false,
    "customer_rank": 1
  }'
```

**Tạo company:**
```bash
curl -X POST http://localhost:5001/api/contacts \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ABC Company",
    "email": "info@abccompany.com",
    "phone": "0241234567",
    "street": "789 Business St",
    "city": "Ho Chi Minh",
    "country_id": 84,
    "is_company": true,
    "customer_rank": 1,
    "supplier_rank": 1
  }'
```

**Response:**
```json
{
  "message": "Tạo contact thành công",
  "id": 2,
  "user": "userTest@gmail.com"
}
```

### 4.4. Update Contact - Cập nhật contact
```bash
curl -X PUT http://localhost:5001/api/contacts/2 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Smith Updated",
    "email": "jane.updated@example.com",
    "phone": "0999999999",
    "street": "456 Park Ave Updated"
  }'
```

**Response:**
```json
{
  "message": "Cập nhật contact thành công",
  "id": 2,
  "user": "userTest@gmail.com"
}
```

### 4.5. Delete Contact - Xóa contact
```bash
curl -X DELETE http://localhost:5001/api/contacts/2 \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "message": "Xóa contact thành công",
  "id": 2,
  "user": "userTest@gmail.com"
}
```

## 5. Complete Workflow Example - Contacts

### Bước 1: Login và lưu token
```bash
RESPONSE=$(curl -s -X POST http://localhost:5001/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "userTest@gmail.com",
    "password": "password"
  }')

TOKEN=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['token'])")
echo "Token: $TOKEN"
```

### Bước 2: Lấy danh sách contacts
```bash
curl -X GET "http://localhost:5001/api/contacts?limit=10" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### Bước 3: Tìm kiếm contacts
```bash
curl -X GET "http://localhost:5001/api/contacts?search=john&limit=10" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### Bước 4: Tạo contact mới
```bash
curl -X POST http://localhost:5001/api/contacts \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Contact",
    "email": "new@example.com",
    "phone": "0123456789",
    "city": "Ho Chi Minh",
    "country_id": 84
  }' | python3 -m json.tool
```

### Bước 5: Lấy thông tin contact cụ thể
```bash
curl -X GET http://localhost:5001/api/contacts/1 \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### Bước 6: Cập nhật contact
```bash
curl -X PUT http://localhost:5001/api/contacts/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Contact Name",
    "email": "updated@example.com"
  }' | python3 -m json.tool
```

### Bước 7: Xóa contact
```bash
curl -X DELETE http://localhost:5001/api/contacts/1 \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

## 6. Users APIs (res.users)

### 6.1. Get All Users - Lấy danh sách users
```bash
curl -X GET "http://localhost:5001/api/users" \
  -H "Authorization: Bearer $TOKEN"
```

**Với query parameters:**
```bash
# Lấy 10 users đầu tiên
curl -X GET "http://localhost:5001/api/users?limit=10&offset=0" \
  -H "Authorization: Bearer $TOKEN"

# Lấy với các fields cụ thể
curl -X GET "http://localhost:5001/api/users?limit=10&offset=0&fields=id,name,login,email,phone" \
  -H "Authorization: Bearer $TOKEN"

# Tìm kiếm users
curl -X GET "http://localhost:5001/api/users?search=john&limit=10" \
  -H "Authorization: Bearer $TOKEN"

# Lấy chỉ active users
curl -X GET "http://localhost:5001/api/users?active=true&limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "data": [
    {
      "id": 2,
      "name": "Administrator",
      "login": "admin@example.com",
      "email": "admin@example.com",
      "phone": "0123456789"
    }
  ],
  "count": 1,
  "user": "userTest@gmail.com"
}
```

### 6.2. Get User by ID - Lấy thông tin 1 user
```bash
curl -X GET http://localhost:5001/api/users/2 \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "data": {
    "id": 2,
    "name": "Administrator",
    "login": "admin@example.com",
    "email": "admin@example.com",
    "phone": "0123456789",
    "active": true,
    "groups_id": [[1, "Administration / Settings"]],
    "is_superuser": true,
    "partner_id": [1, "Administrator"]
  },
  "user": "userTest@gmail.com"
}
```

### 6.3. Create User - Tạo user mới
```bash
curl -X POST http://localhost:5001/api/users \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New User",
    "login": "newuser@example.com",
    "email": "newuser@example.com",
    "phone": "0123456789",
    "active": true
  }'
```

**Response:**
```json
{
  "message": "Tạo user thành công",
  "id": 8,
  "user": "userTest@gmail.com"
}
```

### 6.4. Update User - Cập nhật user
```bash
curl -X PUT http://localhost:5001/api/users/8 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated User Name",
    "email": "updated@example.com",
    "phone": "0999999999"
  }'
```

**Lưu ý:** Không thể cập nhật password qua endpoint này. Phải dùng endpoint change-password.

**Response:**
```json
{
  "message": "Cập nhật user thành công",
  "id": 8,
  "user": "userTest@gmail.com"
}
```

### 6.5. Change Password - Đổi password cho user
```bash
curl -X POST http://localhost:5001/api/users/8/change-password \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "new_password": "newSecurePassword123"
  }'
```

**Response:**
```json
{
  "message": "Đổi password thành công",
  "id": 8,
  "user": "userTest@gmail.com"
}
```

**Lưu ý:**
- User chỉ có thể đổi password của chính mình hoặc phải là superuser/admin
- Password sẽ được hash tự động bởi Odoo

### 6.6. Delete User - Xóa/deactivate user
```bash
curl -X DELETE http://localhost:5001/api/users/8 \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "message": "Deactivate user thành công",
  "id": 8,
  "user": "userTest@gmail.com"
}
```

**Lưu ý:** Trong Odoo, DELETE sẽ deactivate user (set active=False) thay vì xóa hoàn toàn.

## 7. Complete Workflow Example - Users

### Bước 1: Login và lưu token
```bash
RESPONSE=$(curl -s -X POST http://localhost:5001/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "userTest@gmail.com",
    "password": "password"
  }')

TOKEN=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['token'])")
echo "Token: $TOKEN"
```

### Bước 2: Lấy danh sách users
```bash
curl -X GET "http://localhost:5001/api/users?limit=10" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### Bước 3: Tìm kiếm users
```bash
curl -X GET "http://localhost:5001/api/users?search=admin&limit=10" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### Bước 4: Tạo user mới
```bash
curl -X POST http://localhost:5001/api/users \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "login": "testuser@example.com",
    "email": "testuser@example.com",
    "phone": "0123456789"
  }' | python3 -m json.tool
```

### Bước 5: Lấy thông tin user cụ thể
```bash
curl -X GET http://localhost:5001/api/users/8 \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### Bước 6: Cập nhật user
```bash
curl -X PUT http://localhost:5001/api/users/8 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User Updated",
    "email": "test.updated@example.com"
  }' | python3 -m json.tool
```

### Bước 7: Đổi password cho user
```bash
curl -X POST http://localhost:5001/api/users/8/change-password \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "new_password": "NewPassword123"
  }' | python3 -m json.tool
```

### Bước 8: Deactivate user
```bash
curl -X DELETE http://localhost:5001/api/users/8 \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

## 7. Departments APIs (hr.department)

### 7.1. Get All Departments - Lấy danh sách departments
```bash
curl -X GET "http://localhost:5001/api/departments" \
  -H "Authorization: Bearer $TOKEN"
```

**Với query parameters:**
```bash
# Lấy 10 departments đầu tiên
curl -X GET "http://localhost:5001/api/departments?limit=10&offset=0" \
  -H "Authorization: Bearer $TOKEN"

# Lấy với các fields cụ thể
curl -X GET "http://localhost:5001/api/departments?limit=10&offset=0&fields=id,name,manager_id,member_ids" \
  -H "Authorization: Bearer $TOKEN"

# Tìm kiếm departments
curl -X GET "http://localhost:5001/api/departments?search=IT&limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "name": "IT Department",
      "manager_id": [2, "John Manager"],
      "member_ids": [1, 2, 3]
    }
  ],
  "count": 1,
  "user": "userTest@gmail.com"
}
```

### 7.2. Get Department by ID - Lấy thông tin 1 department
```bash
curl -X GET http://localhost:5001/api/departments/1 \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "data": {
    "id": 1,
    "name": "IT Department",
    "manager_id": [2, "John Manager"],
    "member_ids": [1, 2, 3],
    "company_id": [1, "My Company"],
    "parent_id": false,
    "note": "IT Department notes"
  },
  "user": "userTest@gmail.com"
}
```

### 7.3. Create Department - Tạo department mới
```bash
curl -X POST http://localhost:5001/api/departments \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sales Department",
    "manager_id": 2,
    "company_id": 1
  }'
```

**Response:**
```json
{
  "message": "Tạo department thành công",
  "id": 2,
  "user": "userTest@gmail.com"
}
```

### 7.4. Update Department - Cập nhật department
```bash
curl -X PUT http://localhost:5001/api/departments/2 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sales & Marketing Department",
    "manager_id": 3
  }'
```

**Response:**
```json
{
  "message": "Cập nhật department thành công",
  "id": 2,
  "user": "userTest@gmail.com"
}
```

### 7.5. Delete Department - Xóa department
```bash
curl -X DELETE http://localhost:5001/api/departments/2 \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "message": "Xóa department thành công",
  "id": 2,
  "user": "userTest@gmail.com"
}
```

## 8. Complete Workflow Example - Departments

### Bước 1: Login và lưu token
```bash
RESPONSE=$(curl -s -X POST http://localhost:5001/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "userTest@gmail.com",
    "password": "password"
  }')

TOKEN=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['token'])")
echo "Token: $TOKEN"
```

### Bước 2: Lấy danh sách departments
```bash
curl -X GET "http://localhost:5001/api/departments?limit=10" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### Bước 3: Tạo department mới
```bash
curl -X POST http://localhost:5001/api/departments \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "HR Department",
    "manager_id": 2
  }' | python3 -m json.tool
```

### Bước 4: Tạo employee với department
```bash
curl -X POST http://localhost:5001/api/employees \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Employee",
    "work_email": "employee@example.com",
    "work_phone": "0123456789",
    "department_id": 1
  }' | python3 -m json.tool
```

### Bước 5: Lấy employees với department info
```bash
curl -X GET "http://localhost:5001/api/employees?fields=id,name,department_id" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

**Response sẽ bao gồm department_id:**
```json
{
  "data": [
    {
      "id": 1,
      "name": "John Doe",
      "department_id": [1, "IT Department"]
    }
  ],
  "count": 1,
  "user": "userTest@gmail.com"
}
```

### Bước 6: Cập nhật employee department
```bash
curl -X PUT http://localhost:5001/api/employees/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "department_id": 2
  }' | python3 -m json.tool
```

### Bước 7: Cập nhật department
```bash
curl -X PUT http://localhost:5001/api/departments/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "IT & Development Department"
  }' | python3 -m json.tool
```

### Bước 8: Xóa department
```bash
curl -X DELETE http://localhost:5001/api/departments/1 \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

## 9. Approval APIs

### 9.1. Approval Types - Manager Type

#### 9.1.1. Get All Approval Types

```bash
curl -X GET "http://localhost:5001/api/approval/types" \
  -H "Authorization: Bearer $TOKEN"
```

**Với query parameters:**

```bash
# Lấy 10 approval types đầu tiên
curl -X GET "http://localhost:5001/api/approval/types?limit=10&offset=0" \
  -H "Authorization: Bearer $TOKEN"

# Tìm kiếm theo tên
curl -X GET "http://localhost:5001/api/approval/types?search=test&limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

#### 9.1.2. Get Approval Type by ID

```bash
curl -X GET http://localhost:5001/api/approval/types/1 \
  -H "Authorization: Bearer $TOKEN"
```

#### 9.1.3. Create Approval Type

```bash
curl -X POST http://localhost:5001/api/approval/types \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "approval line test",
    "approval_minimum": 2,
    "has_item": true,
    "has_amount": true,
    "has_quantity": true,
    "has_reference": false
  }'
```

#### 9.1.4. Update Approval Type

```bash
curl -X PUT http://localhost:5001/api/approval/types/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "approval line test (updated)",
    "approval_minimum": 1
  }'
```

#### 9.1.5. Delete Approval Type

```bash
curl -X DELETE http://localhost:5001/api/approval/types/1 \
  -H "Authorization: Bearer $TOKEN"
```

### 9.2. Approval Requests - Manager Request Approval

#### 9.2.1. Get All Approval Requests

```bash
curl -X GET "http://localhost:5001/api/approval/requests" \
  -H "Authorization: Bearer $TOKEN"
```

**Với query parameters:**

```bash
# Lấy 10 requests đầu tiên
curl -X GET "http://localhost:5001/api/approval/requests?limit=10&offset=0" \
  -H "Authorization: Bearer $TOKEN"

# Lọc theo trạng thái
curl -X GET "http://localhost:5001/api/approval/requests?status=pending&limit=10" \
  -H "Authorization: Bearer $TOKEN"

# Lọc theo Approval Type
curl -X GET "http://localhost:5001/api/approval/requests?category_id=3&limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

#### 9.2.2. Get Approval Requests To Review (cần user hiện tại duyệt)

```bash
curl -X GET "http://localhost:5001/api/approval/requests/to-review?limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

#### 9.2.3. Get Approval Request by ID

```bash
curl -X GET http://localhost:5001/api/approval/requests/1 \
  -H "Authorization: Bearer $TOKEN"
```

#### 9.2.4. Create Approval Request

```bash
curl -X POST http://localhost:5001/api/approval/requests \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "category_id": 3,
    "name": "approval line test - buy laptop",
    "request_owner_id": 15,
    "request_date": "2026-03-12",
    "amount": 1500.0,
    "reference": "PO-2026-001",
    "reason": "Need laptop for new staff"
  }'
```

#### 9.2.5. Update Approval Request

```bash
curl -X PUT http://localhost:5001/api/approval/requests/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 1800.0,
    "reason": "Need higher spec"
  }'
```

#### 9.2.6. Cancel Approval Request

```bash
curl -X POST http://localhost:5001/api/approval/requests/1/cancel \
  -H "Authorization: Bearer $TOKEN"
```

#### 9.2.7. Approve Approval Request (Manager approve)

```bash
curl -X POST http://localhost:5001/api/approval/requests/1/approve \
  -H "Authorization: Bearer $TOKEN"
```

#### 9.2.8. Reject Approval Request (Manager reject)

```bash
curl -X POST http://localhost:5001/api/approval/requests/1/reject \
  -H "Authorization: Bearer $TOKEN"
```

## 10. Error Handling Examples

### Không có token
```bash
curl -X GET http://localhost:5001/api/employees
# Response: 401 Unauthorized
```

### Token không hợp lệ
```bash
curl -X GET http://localhost:5001/api/employees \
  -H "Authorization: Bearer invalid_token"
# Response: 401 Unauthorized
```

### Không có quyền
```bash
# User không có quyền sẽ nhận 403 Forbidden
curl -X GET http://localhost:5001/api/employees \
  -H "Authorization: Bearer $TOKEN"
# Response: 403 Forbidden nếu không có quyền
```

## 10. Tips

### Format JSON response đẹp hơn
Thêm `| python3 -m json.tool` vào cuối command:
```bash
curl -X GET http://localhost:5001/api/employees \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### Lưu response vào file
```bash
curl -X GET http://localhost:5001/api/employees \
  -H "Authorization: Bearer $TOKEN" > response.json
```

### Verbose mode để debug
```bash
curl -v -X GET http://localhost:5001/api/employees \
  -H "Authorization: Bearer $TOKEN"
```
