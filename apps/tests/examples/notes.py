from testit import helpers as th
from testit import faker

TEST_USER = "testit"
TEST_PWORD = "testit##mojo"


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
    resp = opts.client.get("/api/example/note", params=dict(id=opts.note_pk))
    assert resp.status_code == 200, f"Expected status_code is 200 but got {resp.status_code}"
    assert resp.response.size == 1
    assert resp.response.count == 1
    assert isinstance(resp.response.data, list)
