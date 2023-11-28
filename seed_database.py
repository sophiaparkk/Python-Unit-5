#seeding database means to populate databased with existing data. This uses crud file to input.

import os
import json
from random import choice, randint
from datetime import datetime

import crud
import model
import server
# from server import app

os.system('dropdb -U postgres ratings')
os.system('createdb -U postgres ratings')


model.connect_to_db(server.app)
model.db.create_all()

with open("data/movies.json") as f:
    movie_data = json.loads(f.read())

#we are storing movies from file above into list below
movies_in_db = []
for movie in movie_data:
    title, overview, poster_path = (
        movie["title"],
        movie["overview"],
        movie["poster_path"],
    )
    release_date = datetime.strptime(movie["release_date"], "%Y-%m-%d")

    db_movie = crud.create_movie(title, overview, release_date, poster_path)
    movies_in_db.append(db_movie)

model.db.session.add_all(movies_in_db)
model.db.session.commit()

for n in range(10):
    email = f"user{n}@test.com"
    password = "test"

    user = crud.create_user(email, password)
    model.db.session.add(user)

    for _ in range(10):
        random_movie = choice(movies_in_db)
        score = randint(1, 5)

        rating = crud.create_rating(user, random_movie, score)
        model.db.session.add(rating)

model.db.session.commit()