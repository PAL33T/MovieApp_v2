class Movie:
    def __init__(self, title, director, year, genre, status, rating, description):
        self.title = title
        self.director = director
        self.year = year
        self.genre = genre
        self.status = status
        self.rating = rating
        self.description = description

    def to_dict(self):
        return self.__dict__