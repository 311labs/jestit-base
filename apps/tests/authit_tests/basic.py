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


@th.unit_test("user_save_self")
def test_user_save_self(opts):
    resp = opts.client.login(TEST_USER, TEST_PWORD)
    assert opts.client.is_authenticated, "authentication failed"
    assert opts.client.jwt_data.uid is not None, "missing user id"
    name = faker.fake.last_name()
    resp = opts.client.post(f"/api/authit/user/{opts.client.jwt_data.uid}", dict(display_name=name))
    assert resp.status_code == 200, f"Expected status_code is 200 but got {resp.status_code}"
    assert resp.response.data.display_name == name, f"display_name: {resp.response.data.username }"



@th.unit_test("user_add_perm")
def test_user_add_perm(opts):
    resp = opts.client.login(TEST_USER, TEST_PWORD)
    assert opts.client.is_authenticated, "authentication failed"
    assert opts.client.jwt_data.uid is not None, "missing user id"
    resp = opts.client.post(f"/api/authit/user/{opts.client.jwt_data.uid}", dict(permissions=dict(view_users=True)))
    assert resp.status_code == 403, f"Expected status_code is 403 but got {resp.status_code}"


@th.unit_test("admin_access_user")
def test_admin_access_user(opts):
    resp = opts.client.login(ADMIN_USER, ADMIN_PWORD)
    assert opts.client.is_authenticated, "authentication failed"
    resp = opts.client.get(f"/api/authit/user/{opts.user_id}")
    assert resp.status_code == 200, f"Expected status_code is 200 but got {resp.status_code}"
    assert resp.response.data.id == opts.user_id, f"invalid user id {resp.response.data.id}"
    assert resp.response.data.username == TEST_USER, f"username: {resp.response.data.username }"


@th.unit_test("admin_add_perm")
def test_admin_add_perm(opts):
    # resp = opts.client.login(ADMIN_USER, ADMIN_PWORD)
    assert opts.client.is_authenticated, "authentication failed"
    resp = opts.client.post(f"/api/authit/user/{opts.user_id}", dict(permissions=dict(view_users=True)))
    assert resp.status_code == 200, f"Expected status_code is 200 but got {resp.status_code}"
    assert resp.response.data.id == opts.user_id, f"invalid user id {resp.response.data.id}"
    assert resp.response.data.username == TEST_USER, f"username: {resp.response.data.username }"
    assert resp.response.data.permissions.view_users is True, f"permissions: {resp.response.data.permissions}"


@th.unit_test("admin_remove_perm")
def test_admin_remove_perm(opts):
    # resp = opts.client.login(ADMIN_USER, ADMIN_PWORD)
    assert opts.client.is_authenticated, "authentication failed"
    resp = opts.client.post(f"/api/authit/user/{opts.user_id}", dict(permissions=dict(view_users=None)))
    assert resp.status_code == 200, f"Expected status_code is 200 but got {resp.status_code}"
    assert resp.response.data.id == opts.user_id, f"invalid user id {resp.response.data.id}"
    assert resp.response.data.username == TEST_USER, f"username: {resp.response.data.username }"
    assert resp.response.data.permissions.view_users is None, f"permissions: {resp.response.data.permissions}"


@th.unit_test("admin_add_group")
def test_admin_add_group(opts):
    # resp = opts.client.login(ADMIN_USER, ADMIN_PWORD)
    assert opts.client.is_authenticated, "authentication failed"
    resp = opts.client.post(f"/api/authit/user/{opts.admin_id}", dict(permissions=dict(manage_groups=True)))
    assert resp.status_code == 200, f"Expected status_code is 200 but got {resp.status_code}"
    assert resp.response.data.id == opts.admin_id, f"invalid user id {resp.response.data.id}"
    assert resp.response.data.username == ADMIN_USER, f"username: {resp.response.data.username }"
    assert resp.response.data.permissions.manage_groups is not None, f"permissions: {resp.response.data.permissions}"

    name=faker.generate_name()
    resp = opts.client.post("/api/authit/group", dict(name=name))
    assert resp.status_code == 200, f"Expected status_code is 200 but got {resp.status_code}"
    assert resp.response.data.name == name, f"name: {resp.response.data.name }"
    opts.group_id = resp.response.data.id


@th.unit_test("add_group_member")
def test_add_group_member(opts):
    # resp = opts.client.login(ADMIN_USER, ADMIN_PWORD)
    assert opts.client.is_authenticated, "authentication failed"
    resp = opts.client.post("/api/authit/group/member", dict(user=opts.user_id, group=opts.group_id))
    assert resp.status_code == 200, f"Expected status_code is 200 but got {resp.status_code}"
    assert resp.response.data.user.id == opts.user_id, f"user: {resp.response.data.user.id }"
    assert resp.response.data.group.id == opts.group_id, f"group: {resp.response.data.group.id }"
    opts.member_id = resp.response.data.id
