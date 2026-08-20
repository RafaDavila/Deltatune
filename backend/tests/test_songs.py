from fastapi.testclient import TestClient


def test_list_songs(
    client: TestClient,
) -> None:
    response = client.get("/songs")

    assert response.status_code == 200

    songs = response.json()

    assert len(songs) == 16
    assert songs[0] == {
        "id": 1,
        "title": "Rude Buster",
        "chapter": 1,
    }


def test_filter_songs_by_chapter(
    client: TestClient,
) -> None:
    response = client.get(
        "/songs",
        params={"chapter": 1},
    )

    assert response.status_code == 200

    songs = response.json()

    assert len(songs) == 13
    assert all(
        song["chapter"] == 1
        for song in songs
    )


def test_reject_invalid_chapter(
    client: TestClient,
) -> None:
    response = client.get(
        "/songs",
        params={"chapter": 0},
    )

    assert response.status_code == 422