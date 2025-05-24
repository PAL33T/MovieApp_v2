import json
from datetime import datetime
from movie import Movie

class MovieManager:
    def __init__(self, filename="movies.json"):
        self.filename = filename
        self.movies = []
        self.load()

    def load(self):
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.movies = [Movie(**movie) for movie in data]
        except (FileNotFoundError, json.JSONDecodeError):
            self.movies = []

    def save(self):
        with open(self.filename, "w", encoding="utf-8") as f:
            data = [movie.__dict__ for movie in self.movies]
            json.dump(data, f, ensure_ascii=False, indent=4)

    def add_movie(self, movie):
        self.movies.append(movie)
        self.save()

    def edit_movie(self, index, movie):
        old_status = self.movies[index].status  # stary status filmu
        new_status = movie.status  # nowy status filmu

        if old_status != "Obejrzany" and new_status == "Obejrzany":
            movie.watch_date = datetime.now().strftime("%Y-%m-%d")
        elif new_status != "Obejrzany":
            movie.watch_date = None

        self.movies[index] = movie
        self.save()

    def delete_movie(self, index):
        del self.movies[index]
        self.save()
