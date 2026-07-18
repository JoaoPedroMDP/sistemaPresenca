from __future__ import annotations

from presenca.models import CheckIn


def test_pending_with_valid_code_lists_members_without_checkin(client, code, member):
    response = client.get(f"/api/checkin/pending/{code.code}")

    assert response.status_code == 200
    assert response.json() == {
        "members": [{"id": member.id, "name": member.name}],
    }


def test_pending_can_be_called_twice_with_same_code(client, code, member):
    first = client.get(f"/api/checkin/pending/{code.code}")
    second = client.get(f"/api/checkin/pending/{code.code}")

    assert first.status_code == 200
    assert second.status_code == 200


def test_pending_with_expired_code_returns_400(client, expired_code, member):
    response = client.get(f"/api/checkin/pending/{expired_code.code}")

    assert response.status_code == 400
    assert "expirou" in response.json()["error"]


def test_pending_with_unknown_code_returns_404(client, db):
    response = client.get("/api/checkin/pending/nao-existe")

    assert response.status_code == 404


def test_checkin_creates_checkin_and_returns_points(client, code, member):
    response = client.post(f"/api/checkin/{code.code}/{member.id}")

    assert response.status_code == 200
    assert response.json()["points"] == 50.0
    assert CheckIn.objects.filter(member=member, event=code.event).count() == 1


def test_checkin_twice_same_day_does_not_duplicate(client, code, member):
    first = client.post(f"/api/checkin/{code.code}/{member.id}")
    second = client.post(f"/api/checkin/{code.code}/{member.id}")

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["points"] == first.json()["points"]
    assert CheckIn.objects.filter(member=member, event=code.event).count() == 1


def test_checkin_with_expired_code_returns_400(client, expired_code, member):
    response = client.post(f"/api/checkin/{expired_code.code}/{member.id}")

    assert response.status_code == 400
    assert "expirou" in response.json()["error"]
    assert CheckIn.objects.count() == 0


def test_checkin_with_unknown_code_returns_404(client, member):
    response = client.post(f"/api/checkin/nao-existe/{member.id}")

    assert response.status_code == 404
    assert CheckIn.objects.count() == 0


def test_checkin_with_unknown_member_returns_404(client, code):
    response = client.post(f"/api/checkin/{code.code}/9999")

    assert response.status_code == 404
    assert CheckIn.objects.count() == 0


def test_member_checked_in_leaves_pending_list(client, code, member):
    client.post(f"/api/checkin/{code.code}/{member.id}")

    response = client.get(f"/api/checkin/pending/{code.code}")

    assert response.status_code == 200
    assert response.json() == {"members": []}
