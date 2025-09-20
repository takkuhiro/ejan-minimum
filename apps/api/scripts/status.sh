#!/bin/bash

# Test script for /api/tutorials/{tutorialId}/status endpoint
# This script checks the status of a tutorial generation

API_URL="http://localhost:8000"
ENDPOINT_BASE="/api/tutorials"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check if tutorial ID was provided
if [ $# -eq 0 ]; then
    echo -e "${RED}Error: Tutorial ID required${NC}"
    echo "Usage: $0 <tutorial_id>"
    echo ""
    echo "Example:"
    echo "  $0 tutorial_abc12345"
    echo ""
    echo "You can get a tutorial ID by running:"
    echo "  ./scripts/request.sh"
    exit 1
fi

TUTORIAL_ID="$1"
ENDPOINT="${ENDPOINT_BASE}/${TUTORIAL_ID}/status"

echo -e "${YELLOW}Checking Tutorial Generation Status${NC}"
echo "========================================"
echo "Tutorial ID: ${TUTORIAL_ID}"
echo "Endpoint: ${API_URL}${ENDPOINT}"
echo ""

# Send the request
echo -e "${YELLOW}Fetching status...${NC}"
echo ""

RESPONSE=$(curl -s -X GET "${API_URL}${ENDPOINT}" \
  -H "Accept: application/json" \
  -w "\nHTTP_STATUS_CODE:%{http_code}")

# Extract HTTP status code
HTTP_STATUS=$(echo "${RESPONSE}" | grep "HTTP_STATUS_CODE:" | cut -d':' -f2)
RESPONSE_BODY=$(echo "${RESPONSE}" | sed '/HTTP_STATUS_CODE:/d')

# Check if request was successful
if [ "${HTTP_STATUS}" = "200" ]; then
    echo -e "${GREEN}✓ Status check successful (HTTP ${HTTP_STATUS})${NC}"
    echo ""

    # Parse and display status
    STATUS=$(echo "${RESPONSE_BODY}" | jq -r '.status' 2>/dev/null)
    PROGRESS=$(echo "${RESPONSE_BODY}" | jq -r '.progress' 2>/dev/null)

    # Display overall status with color
    if [ "${STATUS}" = "completed" ]; then
        echo -e "${GREEN}Status: ${STATUS} ✓${NC}"
    elif [ "${STATUS}" = "processing" ]; then
        echo -e "${YELLOW}Status: ${STATUS} ⏳${NC}"
    elif [ "${STATUS}" = "failed" ]; then
        echo -e "${RED}Status: ${STATUS} ✗${NC}"
    else
        echo -e "${CYAN}Status: ${STATUS}${NC}"
    fi

    # Display progress bar
    if [ ! -z "${PROGRESS}" ] && [ "${PROGRESS}" != "null" ]; then
        echo -n "Progress: ["

        # Calculate filled bars (out of 20)
        FILLED=$((PROGRESS * 20 / 100))
        EMPTY=$((20 - FILLED))

        # Draw progress bar
        for i in $(seq 1 $FILLED); do echo -n "█"; done
        for i in $(seq 1 $EMPTY); do echo -n "░"; done

        echo "] ${PROGRESS}%"
    fi

    echo ""
    echo -e "${CYAN}Step Details:${NC}"
    echo "----------------------------------------"

    # Display step information
    STEPS_COUNT=$(echo "${RESPONSE_BODY}" | jq '.steps | length' 2>/dev/null)
    if [ ! -z "${STEPS_COUNT}" ] && [ "${STEPS_COUNT}" -gt 0 ]; then
        for i in $(seq 0 $((STEPS_COUNT - 1))); do
            STEP_NUM=$(echo "${RESPONSE_BODY}" | jq -r ".steps[$i].stepNumber" 2>/dev/null)
            STEP_STATUS=$(echo "${RESPONSE_BODY}" | jq -r ".steps[$i].status" 2>/dev/null)
            VIDEO_URL=$(echo "${RESPONSE_BODY}" | jq -r ".steps[$i].videoUrl" 2>/dev/null)

            # Choose status icon and color
            if [ "${STEP_STATUS}" = "completed" ]; then
                STATUS_ICON="✓"
                STATUS_COLOR="${GREEN}"
            elif [ "${STEP_STATUS}" = "processing" ]; then
                STATUS_ICON="⏳"
                STATUS_COLOR="${YELLOW}"
            elif [ "${STEP_STATUS}" = "pending" ]; then
                STATUS_ICON="○"
                STATUS_COLOR="${CYAN}"
            else
                STATUS_ICON="✗"
                STATUS_COLOR="${RED}"
            fi

            echo -n -e "Step ${STEP_NUM}: ${STATUS_COLOR}${STATUS_ICON} ${STEP_STATUS}${NC}"

            # Show video URL if available
            if [ ! -z "${VIDEO_URL}" ] && [ "${VIDEO_URL}" != "null" ]; then
                echo -e " ${BLUE}[Video ready]${NC}"
            else
                echo ""
            fi
        done
    fi

    echo ""
    echo -e "${CYAN}Full Response:${NC}"
    echo "${RESPONSE_BODY}" | jq '.' 2>/dev/null || echo "${RESPONSE_BODY}"

elif [ "${HTTP_STATUS}" = "404" ]; then
    echo -e "${RED}✗ Tutorial not found (HTTP ${HTTP_STATUS})${NC}"
    echo ""
    echo -e "${RED}Error:${NC}"
    echo "${RESPONSE_BODY}" | jq '.' 2>/dev/null || echo "${RESPONSE_BODY}"
else
    echo -e "${RED}✗ Request failed (HTTP ${HTTP_STATUS})${NC}"
    echo ""
    echo -e "${RED}Error Response:${NC}"
    echo "${RESPONSE_BODY}" | jq '.' 2>/dev/null || echo "${RESPONSE_BODY}"
fi

echo ""
echo "========================================"

# Auto-refresh option
if [ "${STATUS}" = "processing" ] && [ "${HTTP_STATUS}" = "200" ]; then
    echo ""
    echo -e "${YELLOW}Tutorial is still processing.${NC}"
    echo "To auto-refresh status every 5 seconds, run:"
    echo -e "${GREEN}watch -n 5 ./scripts/status.sh ${TUTORIAL_ID}${NC}"
fi