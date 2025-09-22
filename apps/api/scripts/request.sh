#!/bin/bash

# Test script for /api/tutorials/generate endpoint
# This script sends a request to generate a tutorial with raw description

API_URL="http://localhost:8000"
ENDPOINT="/api/tutorials/generate"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Testing Tutorial Generation API${NC}"
echo "========================================"
echo "Endpoint: ${API_URL}${ENDPOINT}"
echo ""

# # Sample request data
# REQUEST_DATA='{
#   "rawDescription": "ナチュラルメイクのチュートリアル。まず、肌を整えるためにファンデーションを薄く塗ります。次に、アイシャドウをベージュ系で自然に仕上げ、最後にリップグロスで唇に潤いを与えます。全体的に清楚で自然な印象を目指します。",
#   "originalImageUrl": "https://storage.googleapis.com/ejan-minimum-storage-dev/IMG_1206.jpg"
# }'


REQUEST_DATA='{"rawDescription":"可愛らしい人形風。若々しく、愛らしいスタイル","originalImageUrl":"https://storage.googleapis.com/ejan-minimum-storage-dev/image_20250921_151428_ae872ca6.jpg","styleId":"75776b63-afda-4892-8af2-bac6e759c609"}'


echo -e "${GREEN}Request Body:${NC}"
echo "${REQUEST_DATA}" | jq '.' 2>/dev/null || echo "${REQUEST_DATA}"
echo ""

echo -e "${YELLOW}Sending request...${NC}"
echo ""

# Send the request and capture response
RESPONSE=$(curl -s -X POST "${API_URL}${ENDPOINT}" \
  -H "Content-Type: application/json" \
  -d "${REQUEST_DATA}" \
  -w "\nHTTP_STATUS_CODE:%{http_code}")

# Extract HTTP status code
HTTP_STATUS=$(echo "${RESPONSE}" | grep "HTTP_STATUS_CODE:" | cut -d':' -f2)
RESPONSE_BODY=$(echo "${RESPONSE}" | sed '/HTTP_STATUS_CODE:/d')

# Check if request was successful
if [ "${HTTP_STATUS}" = "200" ]; then
    echo -e "${GREEN}✓ Request successful (HTTP ${HTTP_STATUS})${NC}"
    echo ""
    echo -e "${GREEN}Response:${NC}"
    echo "${RESPONSE_BODY}" | jq '.' 2>/dev/null || echo "${RESPONSE_BODY}"

    # Extract tutorial ID for use with status.sh
    TUTORIAL_ID=$(echo "${RESPONSE_BODY}" | jq -r '.id' 2>/dev/null)
    if [ ! -z "${TUTORIAL_ID}" ] && [ "${TUTORIAL_ID}" != "null" ]; then
        echo ""
        echo -e "${YELLOW}Tutorial ID: ${TUTORIAL_ID}${NC}"
        echo -e "${YELLOW}You can check the status with:${NC}"
        echo -e "${GREEN}./scripts/status.sh ${TUTORIAL_ID}${NC}"
    fi
else
    echo -e "${RED}✗ Request failed (HTTP ${HTTP_STATUS})${NC}"
    echo ""
    echo -e "${RED}Error Response:${NC}"
    echo "${RESPONSE_BODY}" | jq '.' 2>/dev/null || echo "${RESPONSE_BODY}"
fi

echo ""
echo "========================================"