# app.py
import json
from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
db = SQLAlchemy(app)


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")

class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    genre = fields.Str()
    director_id = fields.Int()
    director = fields.Str()


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()

class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()

movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)

api = Api(app)
movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')

#Возвращаем список всех фильмов
@movie_ns.route('/')
class MovieView(Resource):
    def get(self):
        result = Movie.query.all()
        movies = movies_schema.dump(result)
        return movies

#Возвращаем подробную информацию о фильме
@movie_ns.route('/<int:idx>')
class MovieView(Resource):
    def get(self, idx):
        movie = Movie.query.get(idx)
        return movie_schema.dump(movie)

#Возвращаем только фильмы с определенным режиссером по запросу
@movie_ns.route('/director_id=<int:idx>')
class MovieView(Resource):
    def get(self, idx):

        try:
            result = []
            for movie in Movie.query.all():
                #
                if idx == movie.director_id:
                    result.append(movie)

            return movies_schema.dump(result), 200
        except Exception as e:
            return '', 404

#Возвращаем только фильмы с определенным режиссером и жанром по запросу
@movie_ns.route('/director_id=<int:idx>&genre_id=<int:uid>')
class MovieView(Resource):
    def get(self, idx, uid):
        try:

            result = []
            for movie in Movie.query.all():
                #
                if idx == movie.director_id and uid == movie.genre_id:
                    result.append(movie)
                    #print(result)

            return movies_schema.dump(result), 200
        except Exception as e:
            return '', 404

#Возвращаем только фильмы с определенным жанром по запросу
@movie_ns.route('/genre_id=<int:idx>')
class MovieView(Resource):
    def get(self, idx):
        try:

            result = []
            for movie in Movie.query.all():
                #
                if idx == movie.genre_id:
                    result.append(movie)
                    #print(result)

            return movies_schema.dump(result), 200
        except Exception as e:
            return '', 404

#Возвращаем информацию о режиссерах
@director_ns.route('/')
class DirectorView(Resource):
    def get(self):
        result = Director.query.all()
        directors = directors_schema.dump(result)
        return directors

#Возвращаем только подробную информацию о режиссере
@director_ns.route('/<int:idx>')
class DirectorView(Resource):
    def get(self, idx):
        director = Director.query.get(idx)
        return director_schema.dump(director)

#Возвращаем все жанры
@genre_ns.route('/')
class GenreView(Resource):
    def get(self):
        result = Genre.query.all()
        genres = genres_schema.dump(result)
        return genres

#Возвращаем только информацию о жанре с перечислением списка фильмов по жанру
@genre_ns.route('/<int:idx>')
class GenreView(Resource):
    def get(self, idx):
        genre = Genre.query.get(idx)
        try:

            result = []
            for movie in Movie.query.all():

                if genre.id == movie.genre_id:
                    result.append(movie)


            return movies_schema.dump(result), 200
        except Exception as e:
            return e, 404


if __name__ == '__main__':
    app.run(debug=True)
