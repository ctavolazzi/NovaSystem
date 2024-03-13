/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {
  const collection = new Collection({
    "id": "qq0l4birhdj0gvu",
    "created": "2024-03-10 19:58:24.635Z",
    "updated": "2024-03-10 19:58:24.635Z",
    "name": "ai_chats",
    "type": "base",
    "system": false,
    "schema": [
      {
        "system": false,
        "id": "q8d00hd3",
        "name": "messages",
        "type": "json",
        "required": false,
        "presentable": false,
        "unique": false,
        "options": {
          "maxSize": 2000000
        }
      },
      {
        "system": false,
        "id": "qtiedyxg",
        "name": "description",
        "type": "text",
        "required": false,
        "presentable": false,
        "unique": false,
        "options": {
          "min": null,
          "max": null,
          "pattern": ""
        }
      }
    ],
    "indexes": [],
    "listRule": null,
    "viewRule": null,
    "createRule": null,
    "updateRule": null,
    "deleteRule": null,
    "options": {}
  });

  return Dao(db).saveCollection(collection);
}, (db) => {
  const dao = new Dao(db);
  const collection = dao.findCollectionByNameOrId("qq0l4birhdj0gvu");

  return dao.deleteCollection(collection);
})
