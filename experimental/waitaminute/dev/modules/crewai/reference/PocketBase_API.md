Deletes a single collection Record by its ID.

Depending on the collection's deleteRule value, the access to this action may or may not have been restricted.

You could find individual generated records API documentation from the admin UI.

import PocketBase from 'pocketbase';

const pb = new PocketBase('http://127.0.0.1:8090');

...

await pb.collection('demo').delete('YOUR_RECORD_ID');
DELETE
/api/collections/collectionIdOrName/records/recordId
PATH PARAMETERS
collectionIdOrName	String	ID or name of the record's collection.
recordId	String	ID of the record to delete.


Updates an existing collection Record.

Depending on the collection's updateRule value, the access to this action may or may not have been restricted.

You could find individual generated records API documentation from the admin UI.

import PocketBase from 'pocketbase';

const pb = new PocketBase('http://127.0.0.1:8090');

...

const record = await pb.collection('demo').update('YOUR_RECORD_ID', {
    title: 'Lorem ipsum',
});
PATCH
/api/collections/collectionIdOrName/records/recordId
PATH PARAMETERS
collectionIdOrName	String	ID or name of the record's collection.
recordId	String	ID of the record to update.
BODY PARAMETERS
Schema fields
Any field from the collection's schema.
Auth record fields
Optional
username
String	The username of the auth record.
Optional
email
String	The auth record email address.
This field can be updated only by admins or auth records with "Manage" access.
Regular accounts can update their email by calling "Request email change".
Optional
emailVisibility
Boolean	Whether to show/hide the auth record email when fetching the record data.
Optional
oldPassword
String	Old auth record password.
This field is required only when changing the record password. Admins and auth records with "Manage" access can skip this field.
Optional
password
String	New auth record password.
Optional
passwordConfirm
String	New auth record password confirmation.
Optional
verified
Boolean	Indicates whether the auth record is verified or not.
This field can be set only by admins or auth records with "Manage" access.
Body parameters could be sent as JSON or multipart/form-data.
File upload is supported only through multipart/form-data.
QUERY PARAMETERS
expand	String	Auto expand record relations. Ex.:
?expand=relField1,relField2.subRelField
Supports up to 6-levels depth nested relations expansion.
The expanded relations will be appended to the record under the expand property (eg. "expand": {"relField1": {...}, ...}).
Only the relations to which the request user has permissions to view will be expanded.
fields	String	
Comma separated string of the fields to return in the JSON response (by default returns all fields). Ex.:
?fields=*,expand.relField.name

* targets all keys from the specific depth level.

In addition, the following field modifiers are also supported:

:excerpt(maxLength, withEllipsis?)
Returns a short plain text version of the field string value.
Ex.: ?fields=*,description:excerpt(200,true)
RESPONSES
{
  "@collectionId": "a98f514eb05f454",
  "@collectionName": "demo",
  "id": "ae40239d2bc4477",
  "updated": "2022-06-25 11:03:50.052",
  "created": "2022-06-25 11:03:35.163",
  "title": "Lorem ipsum"
}


Creates a new collection Record.

Depending on the collection's createRule value, the access to this action may or may not have been restricted.

You could find individual generated records API documentation from the admin UI.

import PocketBase from 'pocketbase';

const pb = new PocketBase('http://127.0.0.1:8090');

...

const record = await pb.collection('demo').create({
    title: 'Lorem ipsum',
});
POST
/api/collections/collectionIdOrName/records
PATH PARAMETERS
collectionIdOrName	String	ID or name of the record's collection.
BODY PARAMETERS
Optional
id
String	15 characters string to store as record ID.
If not set, it will be auto generated.
Schema fields
Any field from the collection's schema.
Auth record fields
Optional
username
String	The username of the auth record.
If not set, it will be auto generated.
Optional
email
String	Auth record email address.
Optional
emailVisibility
Boolean	Whether to show/hide the auth record email when fetching the record data.
Required
password
String	Auth record password.
Required
passwordConfirm
String	Auth record password confirmation.
Optional
verified
Boolean	Indicates whether the auth record is verified or not.
This field can be set only by admins or auth records with "Manage" access.
Body parameters could be sent as JSON or multipart/form-data.
File upload is supported only through multipart/form-data.
QUERY PARAMETERS
expand	String	Auto expand record relations. Ex.:
?expand=relField1,relField2.subRelField
Supports up to 6-levels depth nested relations expansion.
The expanded relations will be appended to the record under the expand property (eg. "expand": {"relField1": {...}, ...}).
Only the relations to which the request user has permissions to view will be expanded.
fields	String	
Comma separated string of the fields to return in the JSON response (by default returns all fields). Ex.:
?fields=*,expand.relField.name

* targets all keys from the specific depth level.

In addition, the following field modifiers are also supported:

:excerpt(maxLength, withEllipsis?)
Returns a short plain text version of the field string value.
Ex.: ?fields=*,description:excerpt(200,true)
RESPONSES
{
  "@collectionId": "a98f514eb05f454",
  "@collectionName": "demo",
  "id": "ae40239d2bc4477",
  "updated": "2022-06-25 11:03:50.052",
  "created": "2022-06-25 11:03:35.163",
  "title": "Lorem ipsum"
}


Returns a single collection record by its ID.

Depending on the collection's viewRule value, the access to this action may or may not have been restricted.

You could find individual generated records API documentation in the "Admin UI > Collections > API Preview".

import PocketBase from 'pocketbase';

const pb = new PocketBase('http://127.0.0.1:8090');

...

const record1 = await pb.collection('posts').getOne('RECORD_ID', {
    expand: 'relField1,relField2.subRelField',
});
GET
/api/collections/collectionIdOrName/records/recordId
PATH PARAMETERS
collectionIdOrName	String	ID or name of the record's collection.
recordId	String	ID of the record to view.
QUERY PARAMETERS
expand	String	Auto expand record relations. Ex.:
?expand=relField1,relField2.subRelField
Supports up to 6-levels depth nested relations expansion.
The expanded relations will be appended to the record under the expand property (eg. "expand": {"relField1": {...}, ...}).
Only the relations to which the request user has permissions to view will be expanded.
fields	String	
Comma separated string of the fields to return in the JSON response (by default returns all fields). Ex.:
?fields=*,expand.relField.name

* targets all keys from the specific depth level.

In addition, the following field modifiers are also supported:

:excerpt(maxLength, withEllipsis?)
Returns a short plain text version of the field string value.
Ex.: ?fields=*,description:excerpt(200,true)
RESPONSES
{
  "id": "ae40239d2bc4477",
  "collectionId": "a98f514eb05f454",
  "collectionName": "posts",
  "updated": "2022-06-25 11:03:50.052",
  "created": "2022-06-25 11:03:35.163",
  "title": "test1"
}



Returns a paginated records list, supporting sorting and filtering.

Depending on the collection's listRule value, the access to this action may or may not have been restricted.

You could find individual generated records API documentation in the "Admin UI > Collections > API Preview".

import PocketBase from 'pocketbase';

const pb = new PocketBase('http://127.0.0.1:8090');

...

// fetch a paginated records list
const resultList = await pb.collection('posts').getList(1, 50, {
    filter: 'created >= "2022-01-01 00:00:00" && someField1 != someField2',
});

// you can also fetch all records at once via getFullList
const records = await pb.collection('posts').getFullList({
    sort: '-created',
});

// or fetch only the first record that matches the specified filter
const record = await pb.collection('posts').getFirstListItem('someField="test"', {
    expand: 'relField1,relField2.subRelField',
});
GET
/api/collections/collectionIdOrName/records
PATH PARAMETERS
collectionIdOrName	String	ID or name of the records' collection.
QUERY PARAMETERS
page	Number	The page (aka. offset) of the paginated list (default to 1).
perPage	Number	The max returned records per page (default to 30).
sort	String	
Specify the ORDER BY fields.

Add - / + (default) in front of the attribute for DESC / ASC order, eg.:

// DESC by created and ASC by id
?sort=-created,id
Supported record sort fields:
@random, id, created, updated, and any other field from the collection schema.

filter	String	
Filter expression to filter/search the returned records list (in addition to the collection's listRule), eg.:

?filter=(title~'abc' && created>'2022-01-01')
Supported record filter fields:
id, created, updated, + any field from the collection schema.

The syntax basically follows the format OPERAND OPERATOR OPERAND, where:

OPERAND - could be any of the above field literal, string (single or double quoted), number, null, true, false
OPERATOR - is one of:
= Equal
!= NOT equal
> Greater than
>= Greater than or equal
< Less than
<= Less than or equal
~ Like/Contains (if not specified auto wraps the right string OPERAND in a "%" for wildcard match)
!~ NOT Like/Contains (if not specified auto wraps the right string OPERAND in a "%" for wildcard match)
?= Any/At least one of Equal
?!= Any/At least one of NOT equal
?> Any/At least one of Greater than
?>= Any/At least one of Greater than or equal
?< Any/At least one of Less than
?<= Any/At least one of Less than or equal
?~ Any/At least one of Like/Contains (if not specified auto wraps the right string OPERAND in a "%" for wildcard match)
?!~ Any/At least one of NOT Like/Contains (if not specified auto wraps the right string OPERAND in a "%" for wildcard match)
To group and combine several expressions you could use parenthesis (...), && (AND) and || (OR) tokens.

Single line comments are also supported: // Example comment.

expand	String	Auto expand record relations. Ex.:
?expand=relField1,relField2.subRelField
Supports up to 6-levels depth nested relations expansion.
The expanded relations will be appended to the record under the expand property (eg. "expand": {"relField1": {...}, ...}).
Only the relations to which the request user has permissions to view will be expanded.
fields	String	
Comma separated string of the fields to return in the JSON response (by default returns all fields). Ex.:
?fields=*,expand.relField.name

* targets all keys from the specific depth level.

In addition, the following field modifiers are also supported:

:excerpt(maxLength, withEllipsis?)
Returns a short plain text version of the field string value.
Ex.: ?fields=*,description:excerpt(200,true)
skipTotal	Boolean	If it is set the total counts query will be skipped and the response fields totalItems and totalPages will have -1 value.
This could drastically speed up the search queries when the total counters are not needed or cursor based pagination is used.
For optimization purposes, it is set by default for the getFirstListItem() and getFullList() SDKs methods.
RESPONSES
{
  "page": 1,
  "perPage": 100,
  "totalItems": 2,
  "totalPages": 1,
  "items": [
    {
      "id": "ae40239d2bc4477",
      "collectionId": "a98f514eb05f454",
      "collectionName": "posts",
      "updated": "2022-06-25 11:03:50.052",
      "created": "2022-06-25 11:03:35.163",
      "title": "test1"
    },
    {
      "id": "d08dfc4f4d84419",
      "collectionId": "a98f514eb05f454",
      "collectionName": "posts",
      "updated": "2022-06-25 11:03:45.876",
      "created": "2022-06-25 11:03:45.876",
      "title": "test2"
    }
  ]
}