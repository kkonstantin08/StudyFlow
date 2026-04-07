from datetime import datetime, timezone

from app.models.user import User
from app.services import ai_parser


def test_parse_creates_draft(auth_client):
    response = auth_client.post("/api/v1/ai/parse", json={"raw_text": "Закончить курсовую 2026-04-10 18:00"})
    assert response.status_code == 201
    draft = response.json()
    assert draft["parse_status"] == "parsed"
    assert draft["parse_source"] in {"mistral", "fallback"}
    assert "item" in draft["parsed_payload_json"]


def test_relative_today_uses_users_current_local_date(monkeypatch):
    monkeypatch.setattr(ai_parser, "utc_now", lambda: datetime(2026, 4, 4, 12, 0, tzinfo=timezone.utc))
    parsed, warnings = ai_parser._normalize_item_payload(
        {
            "item_type": "event",
            "title": "Вечерние покатушки с ребятами",
            "description": "Сегодня покатушки с ребятами в 9 вечера",
            "start_at": "2023-11-02T21:00:00+00:00",
            "end_at": None,
            "due_at": None,
            "reminders": [],
        },
        "Сегодня покатушки с ребятами в 9 вечера",
        "Europe/Moscow",
    )

    assert parsed["start_at"] == "2026-04-04T18:00:00+00:00"
    assert any("Relative date was resolved" in warning for warning in warnings)


def test_explicit_date_without_time_defaults_to_9am_local(monkeypatch):
    monkeypatch.setattr(ai_parser, "utc_now", lambda: datetime(2026, 4, 4, 12, 0, tzinfo=timezone.utc))
    parsed, warnings = ai_parser._normalize_item_payload(
        {
            "item_type": "event",
            "title": "Поездка",
            "description": "Поездка 10.04.2026",
            "start_at": "2026-04-10",
            "end_at": None,
            "due_at": None,
            "reminders": [],
        },
        "Поездка 10.04.2026",
        "Europe/Moscow",
    )

    assert parsed["start_at"] == "2026-04-10T06:00:00+00:00"
    assert any("defaulted to 09:00 local time" in warning for warning in warnings)


def test_client_timezone_overrides_user_timezone(monkeypatch):
    monkeypatch.setattr(ai_parser, "utc_now", lambda: datetime(2026, 4, 4, 12, 0, tzinfo=timezone.utc))
    user = User(email="utc@example.com", password_hash="hashed", full_name="UTC User", timezone="UTC")

    parsed, warnings = ai_parser._normalize_item_payload(
        {
            "item_type": "event",
            "title": "Покатушки с ребятами",
            "description": "Сегодня покатушки с ребятами в 9 вечера",
            "start_at": "2026-04-04T21:00:00+00:00",
            "end_at": None,
            "due_at": None,
            "reminders": [],
        },
        "Сегодня покатушки с ребятами в 9 вечера",
        ai_parser._resolve_timezone_name(user, "Europe/Moscow"),
    )

    assert parsed["start_at"] == "2026-04-04T18:00:00+00:00"
    assert any("Relative date was resolved" in warning for warning in warnings)


def test_draft_is_saved_only_after_explicit_confirmation(auth_client):
    draft_response = auth_client.post("/api/v1/ai/parse", json={"raw_text": "Finish database assignment tomorrow at 18:00"})
    assert draft_response.status_code == 201
    draft = draft_response.json()

    items_before_confirmation = auth_client.get("/api/v1/items")
    assert items_before_confirmation.status_code == 200
    assert items_before_confirmation.json() == []

    item_payload = draft["parsed_payload_json"]["item"]
    item_payload["title"] = "Finish database assignment"

    confirm_response = auth_client.post(f"/api/v1/ai/drafts/{draft['id']}/confirm", json={"item": item_payload})
    assert confirm_response.status_code == 200
    assert confirm_response.json()["title"] == "Finish database assignment"
    assert confirm_response.json()["source"] == "ai"

    items_after_confirmation = auth_client.get("/api/v1/items")
    assert items_after_confirmation.status_code == 200
    assert len(items_after_confirmation.json()) == 1

    draft_after_confirmation = auth_client.get(f"/api/v1/ai/drafts/{draft['id']}")
    assert draft_after_confirmation.status_code == 200
    assert draft_after_confirmation.json()["parse_status"] == "confirmed"
    assert draft_after_confirmation.json()["confirmed_at"] is not None
