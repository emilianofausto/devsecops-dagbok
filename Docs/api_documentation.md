# DevSecOps Diary API Documentation

## Overview
This document describes the REST API for the DevSecOps Diary application. The API provides endpoints for Create, Read, Update, and Delete (CRUD) operations on diary entries.

## Base URL
`/api/entries`

## Data Schemas

### `DiaryEntryCreate`
Used for creating a new diary entry.
* **`title`** (string, required): Title of the entry. Minimum length: 1, Maximum length: 100.
* **`content`** (string, required): Main content of the entry. Minimum length: 1.
* **`category`** (string, required): Category of the entry. Minimum length: 1, Maximum length: 50.

### `DiaryEntryUpdate`
Used for modifying an existing diary entry.
* **`title`** (string, optional): Title of the entry. Minimum length: 1, Maximum length: 100.
* **`content`** (string, optional): Main content of the entry. Minimum length: 1.
* **`category`** (string, optional): Category of the entry. Minimum length: 1, Maximum length: 50.

### `DiaryEntryResponse`
Returned by the API after retrieving or modifying an entry.
* **`id`** (integer): Unique identifier for the entry.
* **`title`** (string): Title of the entry.
* **`content`** (string): Main content of the entry.
* **`category`** (string): Category of the entry.
* **`created_at`** (string, ISO 8601 datetime): UTC timestamp of entry creation.

---

## Endpoints

### 1. Get All Entries
Retrieves a list of all diary entries.

* **URL:** `/api/entries`
* **Method:** `GET`
* **Success Response:**
    * **Code:** `200 OK`
    * **Content:** `List[DiaryEntryResponse]`

### 2. Get Single Entry
Retrieves a specific diary entry by its ID.

* **URL:** `/api/entries/{entry_id}`
* **Method:** `GET`
* **Path Parameters:**
    * `entry_id` (integer, required): The ID of the entry to retrieve.
* **Success Response:**
    * **Code:** `200 OK`
    * **Content:** `DiaryEntryResponse`
* **Error Response:**
    * **Code:** `404 Not Found`
    * **Content:** `{"detail": "Entry with ID {entry_id} not found"}`

### 3. Create Entry
Creates a new diary entry.

* **URL:** `/api/entries`
* **Method:** `POST`
* **Request Body:** `DiaryEntryCreate` (application/json)
* **Success Response:**
    * **Code:** `201 Created`
    * **Content:** `DiaryEntryResponse`
* **Error Response:**
    * **Code:** `422 Unprocessable Entity` (Validation Error if schema requirements are not met)

### 4. Update Entry
Updates an existing diary entry. Only provided fields will be modified.

* **URL:** `/api/entries/{entry_id}`
* **Method:** `PUT`
* **Path Parameters:**
    * `entry_id` (integer, required): The ID of the entry to update.
* **Request Body:** `DiaryEntryUpdate` (application/json)
* **Success Response:**
    * **Code:** `200 OK`
    * **Content:** `DiaryEntryResponse`
* **Error Responses:**
    * **Code:** `400 Bad Request`
        * **Content:** `{"detail": "Payload contains no valid modifications"}`
    * **Code:** `404 Not Found`
        * **Content:** `{"detail": "Entry with ID {entry_id} not found"}`

### 5. Delete Entry
Deletes a specific diary entry from the database.

* **URL:** `/api/entries/{entry_id}`
* **Method:** `DELETE`
* **Path Parameters:**
    * `entry_id` (integer, required): The ID of the entry to delete.
* **Success Response:**
    * **Code:** `200 OK`
    * **Content:** `{"message": "Entry {entry_id} successfully deleted"}`
* **Error Response:**
    * **Code:** `404 Not Found`
        * **Content:** `{"detail": "Entry with ID {entry_id} not found"}`
