#!/bin/bash

# Get JWT token from login endpoint
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:5050/login -H "Content-Type: application/json" -d '{"username":"admin","password":"password"}')
TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.token')

echo "Received JWT token: $TOKEN"

# Use the token to call the protected /api/weather endpoint with city parameter
curl -s -G http://localhost:5050/api/weather \
  --data-urlencode "city=London" \
  -H "Authorization: Bearer $TOKEN" | jq
echo
