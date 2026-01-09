# API Reference

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
All endpoints require JWT authentication via Bearer token in the Authorization header.

## Endpoints

### Claims

#### Analyze Claim
```
POST /claims/{claim_id}/analyze
```

Analyzes a claim using AI and returns structured analysis.

**Request Body:**
```json
{
  "claim_id": "CLM-12345",
  "include_member_history": true,
  "include_policy_docs": true
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "claim_id": "CLM-12345",
    "status": "approved",
    "confidence_score": 0.95,
    "recommended_action": "Approve claim",
    "reasoning_steps": [...],
    "policy_sections": [...]
  },
  "processing_time_ms": 1234
}
```

## Error Responses

All errors follow this format:
```json
{
  "success": false,
  "error": "Error message",
  "processing_time_ms": 0
}
```

