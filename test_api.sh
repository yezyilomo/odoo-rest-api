#!/bin/bash

# API Testing Script
# Usage: ./test_api.sh

BASE_URL="http://localhost:5001"
USERNAME="userTest@gmail.com"
PASSWORD="password"

echo "=== API Testing Script ==="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. Health Check
echo -e "${BLUE}1. Health Check${NC}"
curl -s -X GET $BASE_URL/health | python3 -m json.tool
echo ""
echo ""

# 2. Login
echo -e "${BLUE}2. Login${NC}"
LOGIN_RESPONSE=$(curl -s -X POST $BASE_URL/login \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"$USERNAME\",
    \"password\": \"$PASSWORD\"
  }")

echo "$LOGIN_RESPONSE" | python3 -m json.tool

# Extract token
TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('token', ''))" 2>/dev/null)

if [ -z "$TOKEN" ]; then
  echo -e "${RED}Login failed! Please check username and password.${NC}"
  exit 1
fi

echo ""
echo -e "${GREEN}Token saved: ${TOKEN:0:50}...${NC}"
echo ""
echo ""

# 3. Get Current User
echo -e "${BLUE}3. Get Current User (GET /me)${NC}"
curl -s -X GET $BASE_URL/me \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""
echo ""

# 4. Get All Employees
echo -e "${BLUE}4. Get All Employees (GET /api/employees)${NC}"
curl -s -X GET "$BASE_URL/api/employees?limit=10" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""
echo ""

# 5. Get Employee by ID (if employees exist)
echo -e "${BLUE}5. Get Employee by ID (GET /api/employees/1)${NC}"
curl -s -X GET $BASE_URL/api/employees/1 \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""
echo ""

# 6. Create Employee
echo -e "${BLUE}6. Create Employee (POST /api/employees)${NC}"
CREATE_RESPONSE=$(curl -s -X POST $BASE_URL/api/employees \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Employee",
    "work_email": "test.employee@example.com",
    "work_phone": "0123456789"
  }')

echo "$CREATE_RESPONSE" | python3 -m json.tool

# Extract employee ID
EMPLOYEE_ID=$(echo $CREATE_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)
echo ""
echo ""

# 7. Update Employee (if created successfully)
if [ ! -z "$EMPLOYEE_ID" ] && [ "$EMPLOYEE_ID" != "None" ]; then
  echo -e "${BLUE}7. Update Employee (PUT /api/employees/$EMPLOYEE_ID)${NC}"
  curl -s -X PUT $BASE_URL/api/employees/$EMPLOYEE_ID \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "name": "Test Employee Updated",
      "work_email": "test.updated@example.com"
    }' | python3 -m json.tool
  echo ""
  echo ""
  
  # 8. Delete Employee
  echo -e "${BLUE}8. Delete Employee (DELETE /api/employees/$EMPLOYEE_ID)${NC}"
  curl -s -X DELETE $BASE_URL/api/employees/$EMPLOYEE_ID \
    -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
  echo ""
  echo ""
else
  echo -e "${RED}Could not create employee, skipping update and delete${NC}"
fi

# 9. Get All Contacts
echo -e "${BLUE}9. Get All Contacts (GET /api/contacts)${NC}"
curl -s -X GET "$BASE_URL/api/contacts?limit=10" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""
echo ""

# 10. Search Contacts
echo -e "${BLUE}10. Search Contacts (GET /api/contacts?search=test)${NC}"
curl -s -X GET "$BASE_URL/api/contacts?search=test&limit=5" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""
echo ""

# 11. Get Contact by ID
echo -e "${BLUE}11. Get Contact by ID (GET /api/contacts/1)${NC}"
curl -s -X GET $BASE_URL/api/contacts/1 \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""
echo ""

# 12. Create Contact
echo -e "${BLUE}12. Create Contact (POST /api/contacts)${NC}"
CREATE_CONTACT_RESPONSE=$(curl -s -X POST $BASE_URL/api/contacts \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Contact",
    "email": "test.contact@example.com",
    "phone": "0123456789",
    "city": "Ho Chi Minh",
    "country_id": 84
  }')

echo "$CREATE_CONTACT_RESPONSE" | python3 -m json.tool

# Extract contact ID
CONTACT_ID=$(echo $CREATE_CONTACT_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)
echo ""
echo ""

# 13. Update Contact (if created successfully)
if [ ! -z "$CONTACT_ID" ] && [ "$CONTACT_ID" != "None" ]; then
  echo -e "${BLUE}13. Update Contact (PUT /api/contacts/$CONTACT_ID)${NC}"
  curl -s -X PUT $BASE_URL/api/contacts/$CONTACT_ID \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "name": "Test Contact Updated",
      "email": "test.updated@example.com",
      "phone": "0999999999"
    }' | python3 -m json.tool
  echo ""
  echo ""
  
  # 14. Delete Contact
  echo -e "${BLUE}14. Delete Contact (DELETE /api/contacts/$CONTACT_ID)${NC}"
  curl -s -X DELETE $BASE_URL/api/contacts/$CONTACT_ID \
    -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
  echo ""
  echo ""
else
  echo -e "${RED}Could not create contact, skipping update and delete${NC}"
fi

# 15. Get All Users
echo -e "${BLUE}15. Get All Users (GET /api/users)${NC}"
curl -s -X GET "$BASE_URL/api/users?limit=10" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""
echo ""

# 16. Search Users
echo -e "${BLUE}16. Search Users (GET /api/users?search=test)${NC}"
curl -s -X GET "$BASE_URL/api/users?search=test&limit=5" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""
echo ""

# 17. Get User by ID
echo -e "${BLUE}17. Get User by ID (GET /api/users/2)${NC}"
curl -s -X GET $BASE_URL/api/users/2 \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""
echo ""

# 18. Create User
echo -e "${BLUE}18. Create User (POST /api/users)${NC}"
CREATE_USER_RESPONSE=$(curl -s -X POST $BASE_URL/api/users \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "login": "testuser@example.com",
    "email": "testuser@example.com",
    "phone": "0123456789"
  }')

echo "$CREATE_USER_RESPONSE" | python3 -m json.tool

# Extract user ID
USER_ID=$(echo $CREATE_USER_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)
echo ""
echo ""

# 19. Update User (if created successfully)
if [ ! -z "$USER_ID" ] && [ "$USER_ID" != "None" ]; then
  echo -e "${BLUE}19. Update User (PUT /api/users/$USER_ID)${NC}"
  curl -s -X PUT $BASE_URL/api/users/$USER_ID \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "name": "Test User Updated",
      "email": "test.updated@example.com"
    }' | python3 -m json.tool
  echo ""
  echo ""
  
  # 20. Change Password
  echo -e "${BLUE}20. Change Password (POST /api/users/$USER_ID/change-password)${NC}"
  curl -s -X POST $BASE_URL/api/users/$USER_ID/change-password \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "new_password": "NewPassword123"
    }' | python3 -m json.tool
  echo ""
  echo ""
  
  # 21. Delete/Deactivate User
  echo -e "${BLUE}21. Delete/Deactivate User (DELETE /api/users/$USER_ID)${NC}"
  curl -s -X DELETE $BASE_URL/api/users/$USER_ID \
    -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
  echo ""
  echo ""
else
  echo -e "${RED}Could not create user, skipping update, change password and delete${NC}"
fi

# 22. Get All Departments
echo -e "${BLUE}22. Get All Departments (GET /api/departments)${NC}"
curl -s -X GET "$BASE_URL/api/departments?limit=10" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""
echo ""

# 23. Search Departments
echo -e "${BLUE}23. Search Departments (GET /api/departments?search=IT)${NC}"
curl -s -X GET "$BASE_URL/api/departments?search=IT&limit=5" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""
echo ""

# 24. Get Department by ID
echo -e "${BLUE}24. Get Department by ID (GET /api/departments/1)${NC}"
curl -s -X GET $BASE_URL/api/departments/1 \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""
echo ""

# 25. Create Department
echo -e "${BLUE}25. Create Department (POST /api/departments)${NC}"
CREATE_DEPT_RESPONSE=$(curl -s -X POST $BASE_URL/api/departments \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Department",
    "manager_id": 2
  }')

echo "$CREATE_DEPT_RESPONSE" | python3 -m json.tool

# Extract department ID
DEPT_ID=$(echo $CREATE_DEPT_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)
echo ""
echo ""

# 26. Update Department (if created successfully)
if [ ! -z "$DEPT_ID" ] && [ "$DEPT_ID" != "None" ]; then
  echo -e "${BLUE}26. Update Department (PUT /api/departments/$DEPT_ID)${NC}"
  curl -s -X PUT $BASE_URL/api/departments/$DEPT_ID \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "name": "Test Department Updated"
    }' | python3 -m json.tool
  echo ""
  echo ""
  
  # 27. Create Employee with Department
  echo -e "${BLUE}27. Create Employee with Department (POST /api/employees)${NC}"
  curl -s -X POST $BASE_URL/api/employees \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
      \"name\": \"Employee with Dept\",
      \"work_email\": \"empdept@example.com\",
      \"work_phone\": \"0123456789\",
      \"department_id\": $DEPT_ID
    }" | python3 -m json.tool
  echo ""
  echo ""
  
  # 28. Get Employees with Department Info
  echo -e "${BLUE}28. Get Employees with Department Info (GET /api/employees?fields=id,name,department_id)${NC}"
  curl -s -X GET "$BASE_URL/api/employees?fields=id,name,department_id&limit=5" \
    -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
  echo ""
  echo ""
  
  # 29. Delete Department
  echo -e "${BLUE}29. Delete Department (DELETE /api/departments/$DEPT_ID)${NC}"
  curl -s -X DELETE $BASE_URL/api/departments/$DEPT_ID \
    -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
  echo ""
  echo ""
else
  echo -e "${RED}Could not create department, skipping update and delete${NC}"
fi

echo -e "${GREEN}=== Testing Complete ===${NC}"
