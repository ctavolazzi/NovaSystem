# PocketBase CRUD API Documentation

## Introduction
The PocketBase CRUD API allows you to Create, Read, Update, and Delete records in a PocketBase database. This document provides a detailed guide on how to interact with each endpoint. Remember to replace `{token}` with your actual token for authentication and `{id}` with the id of the record you want to interact with.

## Endpoints

### 1. Create Record

**Endpoint**: POST /records

**Header**:
- Content-Type: application/json
- Authorization: Bearer {token}

**Request Body**: 
```json
{
  "field1": "value1",
  "field2": "value2",
  ...
}
```
**Response**: 
- 201 Created (on success)

This endpoint allows you to create a new record. Replace `field1`, `field2`, etc., with the actual field names of the records in the PocketBase database.

### 2. Read Record

**Endpoint**: GET /records/{id}

**Header**:
- Content-Type: application/json
- Authorization: Bearer {token}

**Response**: 
- 200 OK (on success)
- 404 Not Found (if record doesn't exist)

This endpoint allows you to read an existing record by its ID. If the record doesn't exist, you'll receive a 404 Not Found response.

### 3. Update Record

**Endpoint**: PUT /records/{id}

**Header**:
- Content-Type: application/json
- Authorization: Bearer {token}

**Request Body**: 
```json
{
  "field1": "new value1",
  "field2": "new value2",
  ...
}
```
**Response**: 
- 200 OK (on success)
- 404 Not Found (if record doesn't exist)

This endpoint allows you to update an existing record by its ID. Remember to replace `field1`, `field2`, etc., with the actual field names of the records in the PocketBase database.

### 4. Delete Record

**Endpoint**: DELETE /records/{id}

**Header**:
- Content-Type: application/json
- Authorization: Bearer {token}

**Response**: 
- 204 No Content (on success)
- 404 Not Found (if record doesn't exist)

This endpoint allows you to delete an existing record by its ID. If the record doesn't exist, you'll receive a 404 Not Found response.

## Conclusion
This guide provides the basic information required to interact with the PocketBase CRUD API. If you have any issues or need further clarification, please reach out to our support team. Happy Coding!