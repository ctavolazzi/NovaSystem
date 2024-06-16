migrate((db) => {
  const collection = new Collection({
    "id": "r2kkl9z8539l2q3",
    "created": "2023-04-14 02:41:21.169Z",
    "updated": "2023-04-14 02:41:21.169Z",
    "name": "posts",
    "type": "base",
    "system": false,
    "schema": [
      {
        "system": false,
        "id": "pn455gmp",
        "name": "title",
        "type": "text",
        "required": false,
        "unique": false,
        "options": {
          "min": null,
          "max": null,
          "pattern": ""
        }
      },
      {
        "system": false,
        "id": "u0alhmuw",
        "name": "files",
        "type": "file",
        "required": false,
        "unique": false,
        "options": {
          "maxSelect": 99,
          "maxSize": 5242880,
          "mimeTypes": [],
          "thumbs": []
        }
      },
      {
        "system": false,
        "id": "qnfmuolv",
        "name": "body",
        "type": "editor",
        "required": false,
        "unique": false,
        "options": {}
      }
    ],
    "indexes": [
      "CREATE INDEX `_r2kkl9z8539l2q3_created_idx` ON `posts` (`created`)",
      "CREATE INDEX `_r2kkl9z8539l2q3_updated_idx` ON `posts` (`updated`)",
    ],
    "listRule": "",
    "viewRule": "",
    "createRule": "@request.auth.id != \"\"",
    "updateRule": "@request.auth.id != \"\"",
    "deleteRule": null,
    "options": {}
  });

  return Dao(db).saveCollection(collection);
}, (db) => {
  const dao = new Dao(db);
  const collection = dao.findCollectionByNameOrId("r2kkl9z8539l2q3");

  return dao.deleteCollection(collection);
})
