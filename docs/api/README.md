# NovaSystem API Documentation

This directory contains comprehensive documentation for the NovaSystem APIs, including endpoints, request/response formats, authentication, and usage examples.

## API Overview

NovaSystem exposes several APIs for integration and interaction:

1. **REST API** - HTTP-based API for standard request/response interactions
2. **WebSocket API** - Real-time communication for streaming updates
3. **GraphQL API** - (Future) Flexible query language for data retrieval

## REST API

The REST API provides endpoints for managing sessions, users, processes, and resources.

### Base URL

```
https://api.novasystem.io/v1/
```

### Authentication

All API requests require authentication using JWT tokens. Obtain a token by calling the `/auth/login` endpoint.

Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

### Core Endpoints

| Endpoint | Method | Description | Documentation |
|----------|--------|-------------|---------------|
| `/auth/login` | POST | Authenticate user and get token | [Auth API](rest/auth.md) |
| `/auth/refresh` | POST | Refresh authentication token | [Auth API](rest/auth.md) |
| `/sessions` | GET | List user sessions | [Sessions API](rest/sessions.md) |
| `/sessions` | POST | Create new session | [Sessions API](rest/sessions.md) |
| `/sessions/{id}` | GET | Get session details | [Sessions API](rest/sessions.md) |
| `/sessions/{id}/steps` | POST | Execute next step in process | [Steps API](rest/steps.md) |
| `/agents` | GET | List available agents | [Agents API](rest/agents.md) |
| `/templates` | GET | List process templates | [Templates API](rest/templates.md) |
| `/export/{session_id}` | POST | Export session results | [Export API](rest/export.md) |

### Complete REST API Documentation

- [Authentication](rest/auth.md)
- [Sessions](rest/sessions.md)
- [Process Steps](rest/steps.md)
- [Agents](rest/agents.md)
- [Templates](rest/templates.md)
- [Feedback](rest/feedback.md)
- [Export](rest/export.md)
- [Users](rest/users.md)
- [Teams](rest/teams.md)

## WebSocket API

The WebSocket API enables real-time updates and streaming responses for interactive sessions.

### Connection

```
wss://api.novasystem.io/ws/v1?token=<your_jwt_token>
```

### Events

| Event | Direction | Description | Documentation |
|-------|-----------|-------------|---------------|
| `connect` | Client → Server | Initialize connection | [WebSocket API](websocket/connection.md) |
| `join_session` | Client → Server | Join an active session | [WebSocket API](websocket/sessions.md) |
| `user_message` | Client → Server | Send message to session | [WebSocket API](websocket/messages.md) |
| `agent_message` | Server → Client | Receive message from agent | [WebSocket API](websocket/messages.md) |
| `step_progress` | Server → Client | Progress update for step | [WebSocket API](websocket/progress.md) |
| `error` | Server → Client | Error notification | [WebSocket API](websocket/errors.md) |

### Complete WebSocket API Documentation

- [Connection Management](websocket/connection.md)
- [Session Management](websocket/sessions.md)
- [Messaging](websocket/messages.md)
- [Progress Updates](websocket/progress.md)
- [Error Handling](websocket/errors.md)

## API Versioning

The NovaSystem API uses a versioning scheme to ensure backward compatibility:

- **v1** - Initial API version
- **v2** - (Future) Enhanced features and optimizations

## Rate Limiting

API requests are subject to rate limiting to ensure fair usage:

- 100 requests per minute for authenticated users
- 5 requests per minute for unauthenticated users

Rate limit headers are included in all responses:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1628771400
```

## Error Handling

All APIs use standard HTTP status codes and return consistent error objects:

```json
{
  "error": {
    "code": "invalid_request",
    "message": "Invalid request parameters",
    "details": {
      "field": "email",
      "issue": "must be a valid email address"
    },
    "request_id": "req_123abc"
  }
}
```

For common error codes and handling strategies, see [Error Handling](common/errors.md).

## API Tools and SDKs

- [JavaScript SDK](sdks/javascript.md)
- [Python SDK](sdks/python.md)
- [API Playground](tools/playground.md)
- [Postman Collection](tools/postman.md)

## Related Documentation

- [Architecture Documentation](../architecture/README.md)
- [Integration Guides](../guides/integration.md)