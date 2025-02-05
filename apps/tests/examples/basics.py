from testit import helpers as th
from testit import faker


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
    assert resp.response.size == 1
    assert resp.response.count == 1
    assert isinstance(resp.response.data, list)
