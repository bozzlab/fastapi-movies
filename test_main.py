from fastapi.testclient import TestClient
from main import app
import json
import logging

client = TestClient(app)

member_chlid = None
member_mature = None
movie_id_child = None
movie_id_mature = None

def test_register_member_child():
    response = client.post("/api/v1/member", json = {"name" : "Henry", "age" : 12, "phone_number" : "1234"}) 
    global member_chlid
    member_chlid = response.json()['card_id']
    assert response.status_code == 201
    assert isinstance(response.json()['card_id'], str)
    assert len(response.json()['card_id']) == 8

def test_register_member_mature():
    response = client.post("/api/v1/member", json = {"name" : "Nesta", "age" : 22, "phone_number" : "4321"}) 
    global member_mature
    member_mature = response.json()['card_id']
    assert response.status_code == 201
    assert isinstance(response.json()['card_id'], str)
    assert len(response.json()['card_id']) == 8

def test_get_info_member_child():
    response = client.get(f"/api/v1/member?card_id={member_chlid}") 
    assert response.status_code == 200
    assert response.json()['data'][0]['name'] == "Henry"
    assert response.json()['data'][0]['age'] == 12
    assert response.json()['data'][0]['phone_number'] == "1234"
    assert response.json()['data'][0]['role'] == "member"

def test_get_info_member_mature():
    response = client.get(f"/api/v1/member?card_id={member_mature}") 
    assert response.status_code == 200
    assert response.json()['data'][0]['name'] == "Nesta"
    assert response.json()['data'][0]['age'] == 22
    assert response.json()['data'][0]['phone_number'] == "4321"
    assert response.json()['data'][0]['role'] == "member"

def test_get_info_member_not_creatd():
    response = client.get(f"/api/v1/member?card_id=1234") 
    assert response.status_code == 200
    assert response.json()['data'] == "Not found"

def test_get_movies_list_child():
    response = client.get(f"/api/v1/movies", headers = {"X-Card-ID" : f"{member_chlid}"}) 
    assert response.status_code == 200
    assert "adult" not in [movie["genre"] for movie in response.json()["data"]] 

def test_get_movies_list_mature():
    response = client.get(f"/api/v1/movies", headers = {"X-Card-ID" : f"{member_mature}"}) 
    assert response.status_code == 200
    assert "adult" in [movie["genre"] for movie in response.json()["data"]] 

def test_get_movies_list_anonymous():
    response = client.get(f"/api/v1/movies", headers = {"X-Card-ID" : f"1234"}) 
    assert response.status_code == 400
    assert response.json() == {'detail': 'X-Card-ID header invalid'}

def test_new_movies_child():
    response = client.post(f"/api/v1/movies", headers = {"X-Card-ID" : f"{member_chlid}"}, json = {"name" : "Tokyo Diff", "genre" : "action"}) 
    assert response.status_code == 200
    assert response.json()['message'] == 'Tokyo Diff has been added'
    global movie_id_child
    movie_id_child = response.json()['movie_id']

def test_new_movies_mature():
    response = client.post(f"/api/v1/movies", headers = {"X-Card-ID" : f"{member_mature}"}, json = {"name" : "Lolita", "genre" : "adult"}) 
    assert response.status_code == 200
    assert response.json()['message'] == 'Lolita has been added'
    global movie_id_mature
    movie_id_mature = response.json()['movie_id']

def test_new_movies_child_adult():
    response = client.post(f"/api/v1/movies", headers = {"X-Card-ID" : f"{member_chlid}"}, json = {"name" : "Lolita", "genre" : "adult"}) 
    assert response.status_code == 400
    assert response.json() == {"message" : "You cannot insert this movie."}

def test_remove_movies_child():
    response = client.delete(f"/api/v1/movies", headers = {"X-Card-ID" : f"{member_chlid}"}, json = {"name" : "Tokyo Diff", "movie_id" : f"{movie_id_child}"}) 
    assert response.status_code == 200
    assert response.json()['message'] == 'Tokyo Diff has been removed'

def test_remove_movie_error():
    response = client.delete(f"/api/v1/movies", headers = {"X-Card-ID" : f"{member_chlid}"}, json = {"name" : "Hello Diff", "movie_id" : f"{movie_id_child}"}) 
    assert response.status_code == 400
    assert response.json() == {"message" : "Not found."}