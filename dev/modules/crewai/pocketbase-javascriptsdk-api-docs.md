# PocketBase CRUD API Documentation

## Overview
PocketBase is an open-source backend, providing built-in features such as real-time subscriptions, authentication management, file storage and an intuitive dashboard UI.

This API documentation focuses on the Create, Read, Update, and Delete (CRUD) operations, using the `fetch` function for HTTP requests.

## Base API Endpoint and Authorization Token
The base API endpoint and your authorization token are defined at the beginning of your code. Replace `"YOUR_AUTH_TOKEN"` with your actual token.

```javascript
// Define the base API endpoint
const baseApiUrl = "https://pocketbase.io/api/";

// Define your authorization token
const authToken = "YOUR_AUTH_TOKEN";
```

## API Requests
A helper function `makeApiRequest` is used to make API requests. This function takes three parameters:
- `method`: The HTTP method (GET, POST, PUT, DELETE)
- `endpoint`: The specific endpoint for the record you want to interact with
- `body`: The data you want to send in the request body, formatted as a JavaScript object

```javascript
function makeApiRequest(method, endpoint, body = null) {
    const options = {
        method: method,
        headers: {
            'Authorization': `Token ${authToken}`,
            'Content-Type': 'application/json'
        }
    };

    if (body) {
        options.body = JSON.stringify(body);
    }

    return fetch(`${baseApiUrl}${endpoint}`, options)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .catch(e => console.error('Error:', e));
}
```

## CRUD Operations

### Create a Record
To create a record, use the `createRecord` function. This function takes two parameters: 
- `endpoint`: The specific endpoint for the record you want to create
- `data`: The data you want to send in the request body, formatted as a JavaScript object

```javascript
function createRecord(endpoint, data) {
    return makeApiRequest("POST", endpoint, data);
}
```

### Read a Record
To read a record, use the `readRecord` function. This function takes one parameter: 
- `endpoint`: The specific endpoint for the record you want to read

```javascript
function readRecord(endpoint) {
    return makeApiRequest("GET", endpoint);
}
```

### Update a Record
To update a record, use the `updateRecord` function. This function takes two parameters: 
- `endpoint`: The specific endpoint for the record you want to update
- `data`: The data you want to send in the request body, formatted as a JavaScript object

```javascript
function updateRecord(endpoint, data) {
    return makeApiRequest("PUT", endpoint, data);
}
```

### Delete a Record
To delete a record, use the `deleteRecord` function. This function takes one parameter: 
- `endpoint`: The specific endpoint for the record you want to delete

```javascript
function deleteRecord(endpoint) {
    return makeApiRequest("DELETE", endpoint);
}
```

Note: This is a basic outline and does not include error handling or more complex features. You will need to modify this code to fit the specifics of your API and use case.

For more detailed information, please refer to the [official PocketBase documentation](https://pocketbase.io/docs).