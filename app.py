# app.py
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


class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    # genre_id = fields.Int()
    genre = fields.Pluck('GenreSchema', 'name')
    # director_id = fields.Int()
    director = fields.Pluck('DirectorSchema', 'name')


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


# Возвращаем список всех фильмов
@movie_ns.route('/')
class MovieView(Resource):
    def get(self):
        result = Movie.query
        #movies = movies_schema.dump(result)
        director_id = request.args.get("director_id")
        genre_id = request.args.get("genre_id")

        # Возвращаем только фильмы с определенным режиссером по запросу
        if director_id :
            result = result.filter(Movie.director_id == director_id)

        # Возвращаем только фильмы с определенным жанром по запросу
        if genre_id :
            result = result.filter(Movie.genre_id == genre_id)
        return movies_schema.dump(result.all()), 200

    # Добавляем новый фильм
    def post(self):
        data = request.json
        try:
            db.session.add(Movie(**data))
            db.session.commit()
            return "Данные успешно добавлены", 201
        except Exception as e:
            print (e)
            db.session.rollback()
            return "Неудача", 500


# Возвращаем подробную информацию о фильме
@movie_ns.route('/<int:idx>')
class MovieView(Resource):
    def get(self, idx):
        movie = Movie.query.get(idx)
        return movie_schema.dump(movie)

    # Обновляем фильмы с определенным запросом
    def put(self, idx):
        movie = Movie.query.get(idx)
        req_json = request.json
        try:
            movie.title  = req_json.get("title")
            movie.description   = req_json.get("description")
            movie.trailer = req_json.get("trailer")
            movie.year = req_json.get('year')
            movie.rating = req_json.get('rating')
            movie.genre_id = req_json.get('genre_id')
            movie.director_id = req_json.get('director_id')
            db.session.add(movie)
            db.session.commit()
            return "Данные обновлены", 204
        except Exception as e:
            print(e)
            db.session.rollback()
            return "Неудачное обновление", 500

    # Удаляем только фильм с определенным запросом
    def delete(self,idx):
        movie = Movie.query.get(idx)
        db.session.delete(movie)
        db.session.commit()
        return "Данные удалены", 204


# Возвращаем информацию о режиссерах
@director_ns.route('/')
class DirectorView(Resource):
    def get(self):
        result = Director.query.all()
        directors = directors_schema.dump(result)
        return directors

    # Добавляем нового режиссера
    def post(self):
        data = request.json
        try:
            db.session.add(Director(**data))
            db.session.commit()
            return "Данные успешно добавлены", 201
        except Exception as e:
            print(e)
            db.session.rollback()
            return "Неудача", 500

# Возвращаем только подробную информацию о режиссере
@director_ns.route('/<int:idx>')
class DirectorView(Resource):
    def get(self, idx):
        director = Director.query.get(idx)
        return director_schema.dump(director)

    # Обновляем данные режиссера с определенным запросом
    def put(self, idx):
        movie = Director.query.get(idx)
        req_json = request.json
        try:
            movie.name  = req_json.get("name")
            db.session.add(movie)
            db.session.commit()
            return "Данные обновлены", 204
        except Exception as e:
            print(e)
            db.session.rollback()
            return "Неудачное обновление", 500

    # Удаляем режиссера с определенным запросом
    def delete(self,idx):
        movie = Director.query.get(idx)
        db.session.delete(movie)
        db.session.commit()
        return "Данные удалены", 204



# Возвращаем все жанры
@genre_ns.route('/')
class GenreView(Resource):
    def get(self):
        result = Genre.query.all()
        genres = genres_schema.dump(result)
        return genres

        # Добавляем новый жанр
    def post(self):
        data = request.json
        try:
            db.session.add(Genre(**data))
            db.session.commit()
            return "Данные успешно добавлены", 201
        except Exception as e:
            print(e)
            db.session.rollback()
            return "Неудача", 500

# Возвращаем только информацию о жанре с перечислением списка фильмов по жанру
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

    # Обновляем данные жанра с определенным запросом
    def put(self, idx):
        movie = Director.query.get(idx)
        req_json = request.json
        try:
            movie.name  = req_json.get("name")
            db.session.add(movie)
            db.session.commit()
            return "Данные обновлены", 204
        except Exception as e:
            print(e)
            db.session.rollback()
            return "Неудачное обновление", 500

    # Удаляем жанр с определенным запросом
    def delete(self,idx):
        movie = Director.query.get(idx)
        db.session.delete(movie)
        db.session.commit()
        return "Данные удалены", 204


if __name__ == '__main__':
    app.run(debug=True)
