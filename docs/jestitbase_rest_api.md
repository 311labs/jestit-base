# JestitBase REST API Documentation

This document serves as a guide for using the REST API functionalities provided by the `JestitBase` class in Django. The class offers you a structured and generic approach to handle RESTful operations for models with GraphSerializer integration. This guide will walk you through the various endpoints and operations you can perform using this class.

## Overview

The `JestitBase` class allows CRUD operations through REST APIs, incorporating permission checks, filtering, sorting, and serialization of model instances. The class assumes models are Django ORM based and is tightly coupled with Django's request handling and response structures.

## Endpoints and HTTP Methods

### 1. List All Instances

- **Endpoint**: `<base_url>/`
- **Method**: `GET`
- **Description**: Retrieves a list of all instances of the model.
- **Query Parameters**:
  - `sort`: Field to sort by (default is `-id`).
  - Any filter parameters for the model's field.
  - `graph`: Specifies the serialization graph (default is `"list"`).

#### Example Request

```http
GET /api/mymodel/?sort=name&graph=list
```

### 2. Retrieve Single Instance

- **Endpoint**: `<base_url>/<pk>/`
- **Method**: `GET`
- **Description**: Retrieves a single instance of the model.
- **Path Variables**:
  - `pk`: Primary key of the instance.
- **Query Parameters**:
  - `graph`: Specifies the serialization graph (default is `"default"`).

#### Example Request

```http
GET /api/mymodel/123/?graph=detail
```

### 3. Create Instance

- **Endpoint**: `<base_url>/`
- **Method**: `POST`
- **Description**: Creates a new instance of the model.
- **Body**: JSON representation of the model fields and their values.

#### Example Request

```http
POST /api/mymodel/
Content-Type: application/json

{
  "field1": "value1",
  "field2": "value2"
}
```

### 4. Update Instance

- **Endpoint**: `<base_url>/<pk>/`
- **Method**: `PUT`
- **Description**: Updates an existing instance of the model.
- **Path Variables**:
  - `pk`: Primary key of the instance.
- **Body**: JSON representation of the model fields and their updated values.

#### Example Request

```http
PUT /api/mymodel/123/
Content-Type: application/json

{
  "field1": "new value",
  "field2": "updated value"
}
```

### 5. Delete Instance

- **Endpoint**: `<base_url>/<pk>/`
- **Method**: `DELETE`
- **Description**: Deletes an existing instance of the model.
- **Path Variables**:
  - `pk`: Primary key of the instance.

#### Example Request

```http
DELETE /api/mymodel/123/
```

## Permission Requirements

The class incorporates permission checks for safe access:

- `VIEW_PERMS`: Required to view or list instances.
- `SAVE_PERMS`: Required to create or update instances.
- `DELETE_PERMS`: Required to delete instances.
- `CAN_DELETE`: Boolean indicating whether the entity can be deleted.

You must ensure these permissions are appropriately set for the model's RestMeta class or the default behavior is assumed to be restrictive.

## Filtering and Sorting

### Filtering

When querying the list of instances, you can provide any field as a query parameter to filter the results. Foreign key fields can be specified using the `__` notation.

### Sorting

By default, instances are sorted by the descending order of the primary key (`-id`). You can specify a different field with the `sort` query parameter.

## Error Responses

Most methods return a JSON object containing:
- `error`: A description of the error that occurred.
- `code`: HTTP status code of the response.

## Conclusion

The `JestitBase` class simplifies the implementation of REST APIs in Django by providing a standardized method for CRUD operations. This guide should help you leverage the class effectively in your Django applications with permissions, filtering, sorting, and serialization covered comprehensively.

can you add this to the docs folder in this project?
