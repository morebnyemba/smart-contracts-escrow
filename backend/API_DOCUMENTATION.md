# API Documentation

## Seller Search Endpoint

### Search Sellers by Skill

Search for verified sellers that have a specific skill.

**Endpoint:** `GET /api/sellers/search/`

**Query Parameters:**
- `skill` (required): The slug of the skill/service category to filter by

**Response Format:**
```json
[
  {
    "public_seller_id": "uuid",
    "username": "string",
    "account_type": "INDIVIDUAL|COMPANY",
    "company_name": "string|null",
    "verification_status": "VERIFIED",
    "skills": [
      {
        "name": "string",
        "slug": "string"
      }
    ]
  }
]
```

**Example Requests:**

Search for web developers:
```bash
curl "http://localhost:8000/api/sellers/search/?skill=web-development"
```

Search for mobile developers:
```bash
curl "http://localhost:8000/api/sellers/search/?skill=mobile-development"
```

**Success Response:**
- **Status Code:** 200 OK
- **Body:** Array of seller profiles matching the skill

**Error Responses:**

Missing skill parameter:
- **Status Code:** 400 Bad Request
- **Body:** `{"error": "skill query parameter is required"}`

Skill not found:
- **Status Code:** 404 Not Found
- **Body:** `{"error": "Skill \"<skill_slug>\" not found"}`

**Notes:**
- Only VERIFIED sellers are returned in the search results
- Sellers with UNVERIFIED or PENDING verification status are excluded
- Results include all sellers who have the specified skill, even if they have additional skills
- The endpoint uses optimized database queries for performance
