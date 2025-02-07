from testit import helpers as th
from testit import faker

TEST_USER = "testit"
TEST_PWORD = "testit##mojo"


@th.unit_test("create_todo_item")
def test_create_todo_item(opts):
    name = faker.generate_name()
    resp = opts.client.post("/api/example/todo", {
        "name": name,
        "kind":"ticket",
        "description": faker.generate_text()
    })
    assert resp.status_code == 200, f"Expected status_code is 200 but got {resp.status_code}"
    assert resp.response.data.kind == "ticket", f"kind: {resp.response.data.kind }"
    assert resp.response.data.name == name, f"name: {resp.response.data.name }"
    opts.todo_pk = resp.response.data.id


@th.unit_test("get_todo_item")
def test_get_todo_item(opts):
    resp = opts.client.get(f"/api/example/todo/{opts.todo_pk}")
    assert resp.status_code == 200
    assert resp.response.data.id == opts.todo_pk
    assert resp.response.data.kind == "ticket", f"kind: {resp.response.data.kind }"


@th.unit_test("get_todo_item_graph")
def test_get_todo_item_graph(opts):
    resp = opts.client.get(f"/api/example/todo/{opts.todo_pk}", params=dict(graph="basic"))
    assert resp.status_code == 200
    assert resp.response.data.id == opts.todo_pk
    assert resp.response.data.name is not None, f"name: {resp.response.data.name }"
    assert resp.response.data.kind == None, f"kind: {resp.response.data.kind }"


@th.unit_test("update_todo_item")
def test_update_todo_item(opts):
    new_name = faker.generate_name()
    resp = opts.client.post(f"/api/example/todo/{opts.todo_pk}", dict(name=new_name))
    assert resp.status_code == 200, f"Expected status_code is 200 but got {resp.status_code}"
    assert resp.response.data.id == opts.todo_pk
    assert resp.response.data.name == new_name


@th.unit_test("list_todo")
def test_list_todo(opts):
    resp = opts.client.get("/api/example/todo", params=dict(id=opts.todo_pk))
    assert resp.status_code == 200, f"Expected status_code is 200 but got {resp.status_code}"
    assert resp.response.size == 10, f"size is not 10 {resp.response.size}"
    assert resp.response.count == 1, f"count is not 1 {resp.response.count}"
    assert isinstance(resp.response.data, list)


@th.unit_test("get_note_no_user")
def test_get_note(opts):
    resp = opts.client.get(f"/api/example/note")
    assert resp.status_code == 403


@th.unit_test("create_note_no_user")
def test_create_note_no_user(opts):
    name = faker.generate_name()
    resp = opts.client.post("/api/example/note", {
        "name": name,
        "kind":"ticket",
        "description": faker.generate_text()
    })
    assert resp.status_code == 403


@th.unit_test("create_note")
def test_create_note(opts):
    resp = opts.client.login(TEST_USER, TEST_PWORD)

    name = faker.generate_name()
    resp = opts.client.post("/api/example/note", {
        "name": name,
        "kind":"ticket",
        "description": faker.generate_text()
    })
    assert resp.status_code == 200, f"Expected status_code is 200 but got {resp.status_code}"
    assert resp.response.data.kind == "ticket", f"kind: {resp.response.data.kind }"
    assert resp.response.data.name == name, f"name: {resp.response.data.name }"
    opts.note_pk = resp.response.data.id


@th.unit_test("update_note")
def test_update_note(opts):
    new_name = faker.generate_name()
    assert opts.client.is_authenticated, "client not authenticated"
    resp = opts.client.post(f"/api/example/note/{opts.note_pk}", dict(name=new_name))
    assert resp.status_code == 200, f"Expected status_code is 200 but got {resp.status_code}"
    assert resp.response.data.id == opts.note_pk
    assert resp.response.data.name == new_name


@th.unit_test("update_note_metadata")
def test_update_metadata(opts):
    assert opts.client.is_authenticated, "client not authenticated"
    resp = opts.client.post(f"/api/example/note/{opts.note_pk}", dict(metadata=dict(key1="hello", key2="world")))
    assert resp.status_code == 200, f"Expected status_code is 200 but got {resp.status_code}"
    assert resp.response.data.id == opts.note_pk
    assert resp.response.data.metadata == {"key1":"hello", "key2":"world"}


@th.unit_test("remove_note_metadata")
def test_remove_metadata(opts):
    assert opts.client.is_authenticated, "client not authenticated"
    resp = opts.client.post(f"/api/example/note/{opts.note_pk}", dict(metadata=dict(key1=None)))
    assert resp.status_code == 200, f"Expected status_code is 200 but got {resp.status_code}"
    assert resp.response.data.id == opts.note_pk
    assert resp.response.data.metadata == {"key2":"world"}, f"metadata not the same: {resp.response.data.metadata}"


@th.unit_test("list_notes")
def test_list_notes(opts):
    resp = opts.client.get("/api/example/note", params=dict(id=opts.note_pk, size=5))
    assert resp.status_code == 200, f"Expected status_code is 200 but got {resp.status_code}"
    assert resp.response.size == 5, f"size is not 5 {resp.response.size}"
    assert resp.response.count == 1, f"count is not 1 {resp.response.count}"
    assert isinstance(resp.response.data, list)



@th.unit_test("add_note_to_todo")
def test_add_note_to_todo(opts):
    resp = opts.client.post(f"/api/example/todo/{opts.todo_pk}", dict(note=opts.note_pk))
    assert resp.status_code == 200, f"Expected status_code is 200 but got {resp.status_code}"
    assert resp.response.data.note is not None, "has a note"
    assert resp.response.data.note.id == opts.note_pk, "has correct note id"
    assert resp.response.data.note.kind == "ticket", "note kind is ticket"



@th.unit_test("todo_by_note_id")
def test_todo_by_note_id(opts):
    resp = opts.client.get(f"/api/example/todo", params=dict(note__id=opts.note_pk, size=5))
    assert resp.status_code == 200, f"Expected status_code is 200 but got {resp.status_code}"
    assert resp.response.size == 5
    assert resp.response.count == 1
    assert isinstance(resp.response.data, list)
    todo = resp.response.data[0]
    assert todo.id == opts.todo_pk, "has a note"
    assert todo.note.id == opts.note_pk, "has correct note id"
    assert todo.note.kind == "ticket", "note kind is ticket"
