/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {
  const collection = new Collection({
    "id": "agbfyh20i0gf15l",
    "created": "2024-03-10 19:25:30.659Z",
    "updated": "2024-03-10 19:25:30.659Z",
    "name": "crewai_runs",
    "type": "base",
    "system": false,
    "schema": [
      {
        "system": false,
        "id": "0motz4ep",
        "name": "json",
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
        "id": "zdybbtpp",
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
  const collection = dao.findCollectionByNameOrId("agbfyh20i0gf15l");

  return dao.deleteCollection(collection);
})
