from flask import (Flask, render_template, request, flash, session, redirect)
from model import connect_to_db, db, User, Movie, Rating
import crud

from jinja2 import StrictUndefined

app = Flask(__name__)
app.secret_key = "dev"
app.jinja_env.undefined = StrictUndefined


#to view homepage
@app.route('/')
def homepage():

    return render_template('homepage.html')

#to view all movies
@app.route("/movies")
def all_movies():

    movies = crud.get_movies()

    return render_template("all_movies.html", movies=movies)

#to view movie details
@app.route("/movies/<movie_id>")
def show_movie(movie_id):

    movie = crud.get_movie_by_id(movie_id)

    return render_template("movie_details.html", movie=movie)

#to view users
@app.route("/users")
def all_users():

    users = User.all_users()

    return render_template("all_users.html", users=users)

#to create a new user
@app.route("/users", methods=["POST"])
def register_user():

    email = request.form.get("email")
    password = request.form.get("password")

    user = User.get_by_email(email)
    if user:
        flash("This email already exists. Please try again.")
    else:
        user = User.create(email, password)
        db.session.add(user)
        db.session.commit()
        flash("Your account has been created! Please log in.")

    return redirect("/")

#to view user details
@app.route("/users/<user_id>")
def show_user(user_id):

    user = User.get_by_id(user_id)

    return render_template("user_details.html", user=user)

#how user logs in
@app.route("/login", methods=["POST"])
def process_login():

    email = request.form.get("email")
    password = request.form.get("password")

    user = User.get_by_email(email)
    if not user or user.password != password:
        flash("The email or password you entered was incorrect.")
    else:
        #store user's email in a session to log in
        session["user_email"] = user.email
        flash(f"Welcome back, {user.email}!")

    return redirect("/")


#update movie rating
@app.route("/update_rating", methods=["POST"])
def update_rating():
    rating_id = request.json["rating_id"]
    updated_score = request.json["updated_score"]
    Rating.update(rating_id, updated_score)
    db.session.commit()

    return "Success"

#create movie rating
@app.route("/movies/<movie_id>/ratings", methods=["POST"])
def create_rating(movie_id):

    logged_in_email = session.get("user_email")
    rating_score = request.form.get("rating")

    if logged_in_email is None:
        flash("Please log in to rate a movie.")
    elif not rating_score:
        flash("Error: please select a rating score.")
    else:
        user = User.get_by_email(logged_in_email)
        movie = Movie.get_by_id(movie_id)

        rating = Rating.create(user, movie, int(rating_score))
        db.session.add(rating)
        db.session.commit()

        flash(f"You rated this movie {rating_score} out of 5.")

    return redirect(f"/movies/{movie_id}")


if __name__ == '__main__':
    connect_to_db(app)
    app.run(host='0.0.0.0', debug=True)
