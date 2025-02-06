from testit import helpers as th
from testit import faker

TEST_USER = "testit"
TEST_PWORD = "testit##mojo"

ADMIN_USER = "tadmin"
ADMIN_PWORD = "testit##mojo"


@th.unit_test("user_jwt_login")
def test_user_jwt_login(opts):
    resp = opts.client.login(TEST_USER, TEST_PWORD)
    assert opts.client.is_authenticated, "authentication failed"
    assert opts.client.jwt_data.uid is not None, "missing user id"
    resp = opts.client.get(f"/api/authit/user/{opts.client.jwt_data.uid}")
    assert resp.status_code == 200, f"Expected status_code is 200 but got {resp.status_code}"
    assert resp.response.data.id == opts.client.jwt_data.uid
    assert resp.response.data.username == TEST_USER, f"username: {resp.response.data.username }"
    opts.user_id = opts.client.jwt_data.uid

@th.unit_test("admin_jwt_login")
def test_admin_jwt_login(opts):
    resp = opts.client.login(ADMIN_USER, ADMIN_PWORD)
    assert opts.client.is_authenticated, "authentication failed"
    assert opts.client.jwt_data.uid is not None, "missing user id"
    resp = opts.client.get(f"/api/authit/user/{opts.client.jwt_data.uid}")
    assert resp.status_code == 200, f"Expected status_code is 200 but got {resp.status_code}"
    assert resp.response.data.id == opts.client.jwt_data.uid, f"invalid user id {resp.response.data.id}"
    assert resp.response.data.username == ADMIN_USER, f"username: {resp.response.data.username }"
    opts.admin_id = opts.client.jwt_data.uid

@th.unit_test("user_access_admin")
def test_user_access_admin(opts):
    resp = opts.client.login(TEST_USER, TEST_PWORD)
    assert opts.client.is_authenticated, "authentication failed"
    assert opts.client.jwt_data.uid is not None, "missing user id"
    resp = opts.client.get(f"/api/authit/user/{opts.admin_id}")
    assert resp.status_code == 403, f"Expected status_code is 403 but got {resp.status_code}"


@th.unit_test("admin_access_user")
def test_admin_access_user(opts):
    resp = opts.client.login(ADMIN_USER, ADMIN_PWORD)
    assert opts.client.is_authenticated, "authentication failed"
    resp = opts.client.get(f"/api/authit/user/{opts.user_id}")
    assert resp.status_code == 200, f"Expected status_code is 200 but got {resp.status_code}"
    assert resp.response.data.id == opts.user_id, f"invalid user id {resp.response.data.id}"
    assert resp.response.data.username == TEST_USER, f"username: {resp.response.data.username }"
