
import pytest
import json
from model_bakery import baker


@pytest.mark.django_db
class TestLibraryAPI:
    def test_get_libraries(self, client):
        baker.make("library.Library", 5)
        r = client.get("/api/library/")
        data = r.json()
        assert r.status_code == 200
        assert len(data) == 5

    def test_create_library(self, client):
        payload = {"name": "Городская библиотека", "address": "ул. Ленина, 10"}
        r = client.post("/api/library/", json.dumps(payload), content_type="application/json")
        assert r.status_code == 201
        data = r.json()
        assert data["name"] == "Городская библиотека"

    def test_update_library(self, client):
        lib = baker.make("library.Library")
        payload = {"name": "Новая библиотека", "address": "ул. Чехова, 5"}
        r = client.put(f"/api/library/{lib.id}/", json.dumps(payload), content_type="application/json")
        assert r.status_code == 200
        data = r.json()
        assert data["name"] == "Новая библиотека"


@pytest.mark.django_db
class TestGenreAPI:
    def test_get_genres(self, client):
        baker.make("library.Genre", 4)
        r = client.get("/api/genre/")
        data = r.json()
        assert r.status_code == 200
        assert len(data) == 4

    def test_create_genre(self, client):
        payload = {"name": "Фантастика"}
        r = client.post("/api/genre/", json.dumps(payload), content_type="application/json")
        assert r.status_code == 201
        assert r.json()["name"] == "Фантастика"

    def test_update_genre(self, client):
        genre = baker.make("library.Genre")
        payload = {"name": "Детектив"}
        r = client.put(f"/api/genre/{genre.id}/", json.dumps(payload), content_type="application/json")
        assert r.status_code == 200
        assert r.json()["name"] == "Детектив"


@pytest.mark.django_db
class TestBookAPI:
    def test_get_books(self, client):
        baker.make("library.Book", 5)
        r = client.get("/api/book/")
        data = r.json()
        assert r.status_code == 200
        assert len(data) == 5

    def test_create_book(self, client):
        genre = baker.make("library.Genre")
        library = baker.make("library.Library")
        payload = {"title": "1984", "genre": genre.id, "library": library.id}
        r = client.post("/api/book/", json.dumps(payload), content_type="application/json")
        assert r.status_code == 201
        assert r.json()["title"] == "1984"

    def test_update_book(self, client):
        book = baker.make("library.Book")
        payload = {"title": "Animal Farm", "genre": book.genre.id, "library": book.library.id}
        r = client.put(f"/api/book/{book.id}/", json.dumps(payload), content_type="application/json")
        assert r.status_code == 200
        assert r.json()["title"] == "Animal Farm"


@pytest.mark.django_db
class TestMemberAPI:
    def test_get_members(self, client):
        baker.make("library.Member", 6)
        r = client.get("/api/member/")
        data = r.json()
        assert r.status_code == 200
        assert len(data) == 6

    def test_create_member(self, client):
        library = baker.make("library.Library")
        payload = {"first_name": "Иван", "library": library.id}
        r = client.post("/api/member/", json.dumps(payload), content_type="application/json")
        assert r.status_code == 201
        assert r.json()["first_name"] == "Иван"

    def test_update_member(self, client):
        member = baker.make("library.Member")
        payload = {"first_name": "Петр", "library": member.library.id}
        r = client.put(f"/api/member/{member.id}/", json.dumps(payload), content_type="application/json")
        assert r.status_code == 200
        assert r.json()["first_name"] == "Петр"


@pytest.mark.django_db
class TestLoanAPI:
    def test_get_loans(self, client):
        baker.make("library.Loan", 3)
        r = client.get("/api/loan/")
        data = r.json()
        assert r.status_code == 200
        assert len(data) == 3

    def test_create_loan(self, client):
        book = baker.make("library.Book")
        member = baker.make("library.Member")
        payload = {"book": book.id, "member": member.id, "loan_date": "2024-10-01"}
        r = client.post("/api/loan/", json.dumps(payload), content_type="application/json")
        assert r.status_code == 201
        assert r.json()["loan_date"] == "2024-10-01"

    def test_update_loan(self, client):
        loan = baker.make("library.Loan")
        payload = {"book": loan.book.id, "member": loan.member.id, "loan_date": "2024-12-31"}
        r = client.put(f"/api/loan/{loan.id}/", json.dumps(payload), content_type="application/json")
        assert r.status_code == 200
        assert r.json()["loan_date"] == "2024-12-31"