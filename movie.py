class InvalidRatingError(Exception):
    pass

class Movie:
    def __init__(self, title, director, year, genre, status, rating=None, _rating=None, description="", watch_date=None):
        self.title = title
        self.director = director
        self.year = year
        self.genre = genre
        self.status = status
        self.rating = rating if rating is not None else _rating
        self.description = description
        self.watch_date = watch_date
