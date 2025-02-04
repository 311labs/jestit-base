from testit import helpers as th
import testit.client
from testit import faker
from jestit.helpers import logit

TEST_CLIENT = None

def get_client(opts):
    global TEST_CLIENT
    if TEST_CLIENT is None:
        TEST_CLIENT = testit.client.RestClient(opts.host, logger=logit.get_logger("testit", "testit.log"))
    return TEST_CLIENT


@th.unit_test("create_todo_item")
def test_create_todo_item(opts):
    client = get_client(opts)
    name = faker.generate_name()
    resp = client.post("/api/example/todo", {
        "name": name,
        "kind":"ticket",
        "description": faker.generate_text()
    })
    TEST_CLIENT.logger.info(resp)
    assert resp.status_code == 200, f"Expected status_code is 200 but got {resp.status_code}"
    assert resp.response.data.kind == "ticket", f"kind: {resp.response.data.kind }"
    assert resp.response.data.name == name, f"name: {resp.response.data.name }"
    opts.todo_pk = resp.response.data.id


@th.unit_test("get_todo_item")
def test_get_todo_item(opts):
    client = get_client(opts)
    resp = client.get(f"/api/example/todo/{opts.todo_pk}")
    assert resp.status_code == 200
    assert resp.response.data.id == opts.todo_pk


@th.unit_test("update_todo_item")
def test_update_todo_item(opts):
    client = get_client(opts)
    new_name = faker.generate_name()
    resp = client.post(f"/api/example/todo/{opts.todo_pk}", dict(name=new_name))
    assert resp.status_code == 200, f"Expected status_code is 200 but got {resp.status_code}"
    assert resp.response.data.id == opts.todo_pk
    assert resp.response.data.name == new_name


@th.unit_test("list_todo")
def test_list_todo(opts):
    client = get_client(opts)
    resp = client.get("/api/example/todo", params=dict(id=opts.todo_pk))
    assert resp.status_code == 200, f"Expected status_code is 200 but got {resp.status_code}"
    assert resp.response.size == 1
    assert resp.response.count == 1
    assert isinstance(resp.response.data, list)
