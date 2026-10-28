import pytest
from app import app as flask_app


@pytest.fixture()
def client(tmp_path):
    db_path = tmp_path / "test_community_help.db"
    flask_app.config.update(TESTING=True, DATABASE=str(db_path), SECRET_KEY="test-secret")
    with flask_app.test_client() as test_client:
        yield test_client


def create_request(client, title="Need maths tutoring", category="Education"):
    return client.post("/request-help", data={
        "title": title,
        "description": "Looking for a volunteer tutor for basic maths.",
        "category": category,
        "location": "North neighbourhood",
        "requester": "Community Member",
    }, follow_redirects=True)


def test_home_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Stronger communities" in response.data


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "ok"


def test_valid_request_is_created(client):
    response = create_request(client)
    assert response.status_code == 200
    assert b"Need maths tutoring" in response.data
    assert b"Your help request was submitted." in response.data


def test_invalid_request_is_rejected(client):
    response = client.post("/request-help", data={
        "title": "", "description": "", "category": "Unknown",
        "location": "", "requester": "",
    })
    assert response.status_code == 400
    assert b"Choose a valid category." in response.data


def test_volunteer_can_accept_open_request(client):
    create_request(client)
    with flask_app.app_context():
        from app import get_db
        request_id = get_db().execute("SELECT id FROM help_requests").fetchone()["id"]
    response = client.post(f"/requests/{request_id}/accept",
                           data={"volunteer": "Volunteer One"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Volunteer One" in response.data
    assert b"Accepted" in response.data


def test_closed_request_cannot_be_accepted_twice(client):
    create_request(client)
    with flask_app.app_context():
        from app import get_db
        request_id = get_db().execute("SELECT id FROM help_requests").fetchone()["id"]
    client.post(f"/requests/{request_id}/accept", data={"volunteer": "Volunteer One"})
    response = client.post(f"/requests/{request_id}/accept",
                           data={"volunteer": "Volunteer Two"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"no longer open" in response.data


def test_accepted_request_can_be_completed(client):
    create_request(client)
    with flask_app.app_context():
        from app import get_db
        request_id = get_db().execute("SELECT id FROM help_requests").fetchone()["id"]
    client.post(f"/requests/{request_id}/accept", data={"volunteer": "Volunteer One"})
    response = client.post(f"/requests/{request_id}/complete", follow_redirects=True)
    assert response.status_code == 200
    assert b"Request marked as completed." in response.data
    assert b"Completed" in response.data
