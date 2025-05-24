import tkinter as tk
from tkinter import ttk, messagebox
from movie import Movie
from movie_manager import MovieManager

class MovieApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Movie Manager")

        self.manager = MovieManager()
        self.filtered_movies = []

        self.selected_index = None
        self.sort_column = None
        self.sort_reverse = False

        # Vars for input fields
        self.vars = [tk.StringVar() for _ in range(7)]
        (self.title_var, self.director_var, self.year_var,
         self.genre_var, self.status_var, self.rating_var, self.desc_var) = self.vars

        # Filters
        self.search_var = tk.StringVar()
        self.filter_status = tk.StringVar()
        self.filter_genre = tk.StringVar()
        self.filter_director = tk.StringVar()
        self.filter_year = tk.StringVar()

        self.setup_ui()
        self.reset_filters()

    def setup_ui(self):
        frm = ttk.Frame(self.root)
        frm.pack(padx=10, pady=10, fill="both", expand=True)

        # Input fields
        labels = ["Tytuł", "Reżyser", "Rok", "Gatunek", "Status", "Ocena", "Opis"]
        for i, text in enumerate(labels):
            ttk.Label(frm, text=text).grid(row=i, column=0, sticky="w", pady=2)
        for i, var in enumerate(self.vars):
            if i == 6:
                ttk.Entry(frm, textvariable=var, width=50).grid(row=i, column=1, sticky="ew", pady=2)
            else:
                ttk.Entry(frm, textvariable=var).grid(row=i, column=1, sticky="ew", pady=2)
        frm.columnconfigure(1, weight=1)

        # Buttons
        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=7, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Dodaj", command=self.add_movie).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Edytuj", command=self.edit_movie).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Usuń", command=self.delete_movie).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Wyczyść pola", command=self.clear_fields).pack(side="left", padx=5)

        # Filters UI
        filter_frame = ttk.LabelFrame(self.root, text="Filtry")
        filter_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(filter_frame, text="Tytuł:").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Entry(filter_frame, textvariable=self.search_var).grid(row=0, column=1, sticky="ew", pady=2)

        ttk.Label(filter_frame, text="Status:").grid(row=0, column=2, sticky="w", pady=2)
        self.status_cb = ttk.Combobox(filter_frame, textvariable=self.filter_status, state="readonly")
        self.status_cb.grid(row=0, column=3, sticky="ew", pady=2)

        ttk.Label(filter_frame, text="Gatunek:").grid(row=1, column=0, sticky="w", pady=2)
        self.genre_cb = ttk.Combobox(filter_frame, textvariable=self.filter_genre, state="readonly")
        self.genre_cb.grid(row=1, column=1, sticky="ew", pady=2)

        ttk.Label(filter_frame, text="Reżyser:").grid(row=1, column=2, sticky="w", pady=2)
        self.director_cb = ttk.Combobox(filter_frame, textvariable=self.filter_director, state="readonly")
        self.director_cb.grid(row=1, column=3, sticky="ew", pady=2)

        ttk.Label(filter_frame, text="Rok:").grid(row=2, column=0, sticky="w", pady=2)
        self.year_cb = ttk.Combobox(filter_frame, textvariable=self.filter_year, state="readonly")
        self.year_cb.grid(row=2, column=1, sticky="ew", pady=2)

        ttk.Button(filter_frame, text="Filtruj", command=self.apply_filters).grid(row=2, column=2, sticky="ew", pady=2)
        ttk.Button(filter_frame, text="Resetuj filtry", command=self.reset_filters).grid(row=2, column=3, sticky="ew", pady=2)

        for i in range(4):
            filter_frame.columnconfigure(i, weight=1)

        # Treeview
        columns = ("Tytuł", "Rok", "Gatunek", "Status", "Ocena")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", selectmode="browse")
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
            self.tree.column(col, minwidth=50, width=100)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def add_movie(self):
        movie = self.get_movie_from_fields()
        if not movie:
            return
        try:
            self.manager.add_movie(movie)
            self.clear_fields()
            self.reset_filters()
            messagebox.showinfo("Sukces", "Film dodany.")
        except ValueError as e:
            messagebox.showerror("Błąd", str(e))

    def edit_movie(self):
        if self.selected_index is None:
            messagebox.showwarning("Brak wyboru", "Wybierz film do edycji.")
            return
        movie = self.get_movie_from_fields()
        if not movie:
            return
        actual_index = self.manager.movies.index(self.filtered_movies[self.selected_index])
        try:
            self.manager.edit_movie(actual_index, movie)
            self.clear_fields()
            self.reset_filters()
            messagebox.showinfo("Sukces", "Film edytowany.")
        except (ValueError, IndexError) as e:
            messagebox.showerror("Błąd", str(e))

    def delete_movie(self):
        if self.selected_index is None:
            messagebox.showwarning("Brak wyboru", "Wybierz film do usunięcia.")
            return
        actual_index = self.manager.movies.index(self.filtered_movies[self.selected_index])
        try:
            self.manager.delete_movie(actual_index)
            self.clear_fields()
            self.reset_filters()
            messagebox.showinfo("Sukces", "Film usunięty.")
        except IndexError as e:
            messagebox.showerror("Błąd", str(e))

    def get_movie_from_fields(self):
        try:
            year = int(self.year_var.get())
        except ValueError:
            messagebox.showerror("Błąd", "Rok musi być liczbą całkowitą.")
            return None

        try:
            rating = float(self.rating_var.get())
            if not (0 <= rating <= 10):
                raise ValueError("Ocena musi być od 0 do 10.")
        except ValueError as e:
            messagebox.showerror("Błąd", f"Błędne dane: {e}")
            return None

        title = self.title_var.get().strip()
        director = self.director_var.get().strip()
        genre = self.genre_var.get().strip()
        status = self.status_var.get().strip()
        description = self.desc_var.get().strip()
        if not title or not director or not genre or not status:
            messagebox.showerror("Błąd", "Wypełnij wszystkie pola oprócz opisu.")
            return None
        return Movie(title, director, year, genre, status, rating, description)

    def clear_fields(self):
        for var in self.vars:
            var.set("")
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())
        self.selected_index = None

    def refresh_movie_list(self):
        # Zapamiętaj aktualny zaznaczony tytuł i rok, by po odświeżeniu przywrócić zaznaczenie
        selected_movie = None
        if self.selected_index is not None and 0 <= self.selected_index < len(self.filtered_movies):
            selected_movie = self.filtered_movies[self.selected_index]

        self.tree.delete(*self.tree.get_children())
        for movie in self.filtered_movies:
            self.tree.insert("", "end", values=(
                movie.title, movie.year, movie.genre, movie.status, movie.rating))

        # Przywróć zaznaczenie jeśli to możliwe
        if selected_movie:
            for iid in self.tree.get_children():
                item = self.tree.item(iid)
                vals = item['values']
                if vals[0] == selected_movie.title and vals[1] == selected_movie.year:
                    self.tree.selection_set(iid)
                    break

    def apply_filters(self):
        title_filter = self.search_var.get().lower()
        status_filter = self.filter_status.get()
        genre_filter = self.filter_genre.get()
        director_filter = self.filter_director.get()
        year_filter = self.filter_year.get()

        self.filtered_movies = []
        for m in self.manager.movies:
            if title_filter and title_filter not in m.title.lower():
                continue
            if status_filter and m.status != status_filter:
                continue
            if genre_filter and m.genre != genre_filter:
                continue
            if director_filter and m.director != director_filter:
                continue
            if year_filter and str(m.year) != year_filter:
                continue
            self.filtered_movies.append(m)

        self.sort_column = None
        self.sort_reverse = False
        self.refresh_movie_list()
        self.update_filter_options()

    def reset_filters(self):
        self.search_var.set("")
        self.filter_status.set("")
        self.filter_genre.set("")
        self.filter_director.set("")
        self.filter_year.set("")
        self.filtered_movies = self.manager.movies[:]
        self.refresh_movie_list()
        self.update_filter_options()

    def update_filter_options(self):
        statuses = sorted(set(m.status for m in self.manager.movies))
        genres = sorted(set(m.genre for m in self.manager.movies))
        directors = sorted(set(m.director for m in self.manager.movies))
        years = sorted(set(str(m.year) for m in self.manager.movies))

        self.status_cb['values'] = [""] + statuses
        self.genre_cb['values'] = [""] + genres
        self.director_cb['values'] = [""] + directors
        self.year_cb['values'] = [""] + years

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected:
            self.selected_index = None
            self.clear_fields()
            return
        item = self.tree.item(selected[0])
        values = item['values']
        for idx, movie in enumerate(self.filtered_movies):
            if movie.title == values[0] and str(movie.year) == str(values[1]):
                self.selected_index = idx
                self.load_movie_into_fields(movie)
                break

    def load_movie_into_fields(self, movie):
        self.title_var.set(movie.title)
        self.director_var.set(movie.director)
        self.year_var.set(str(movie.year))
        self.genre_var.set(movie.genre)
        self.status_var.set(movie.status)
        self.rating_var.set(str(movie.rating))
        self.desc_var.set(movie.description)

    def sort_by_column(self, col):
        col_map = {
            "Tytuł": lambda m: m.title.lower(),
            "Rok": lambda m: m.year,
            "Gatunek": lambda m: m.genre.lower(),
            "Status": lambda m: m.status.lower(),
            "Ocena": lambda m: m.rating,
        }
        if col == self.sort_column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = col
            self.sort_reverse = False
        key_func = col_map.get(col)
        if key_func:
            self.filtered_movies.sort(key=key_func, reverse=self.sort_reverse)
            self.refresh_movie_list()
