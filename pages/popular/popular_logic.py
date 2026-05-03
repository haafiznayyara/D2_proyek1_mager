# popular_logic.py
from difflib import SequenceMatcher

from database.connection import connection_database


FUZZY_THRESHOLD = 0.72


def get_popular_games(order: str = "desc") -> list:
    """
    Ambil game dari DB dan urutkan berdasarkan peak_player.

    order:
        "desc" → tertinggi dulu
        "asc"  → terendah dulu
    """
    direction = "DESC" if order.lower() == "desc" else "ASC"

    try:
        conn = connection_database()
        cursor = conn.cursor()

        cursor.execute(f"""
            SELECT g.*,
                   GROUP_CONCAT(gr.nama_genre SEPARATOR '||') AS genres_str
            FROM game g
            LEFT JOIN detail_genre dg ON g.id_game = dg.id_game
            LEFT JOIN genre gr ON dg.id_genre = gr.id_genre
            GROUP BY g.id_game
            ORDER BY g.peak_player {direction}
        """)

        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        games = []

        for row in rows:
            good = int(row.get("good_review") or 0)
            bad = int(row.get("bad_review") or 0)
            total = good + bad
            rating = round(good / total * 100) if total > 0 else 0

            genres_str = row.get("genres_str") or ""
            genres = [
                genre.strip()
                for genre in genres_str.split("||")
                if genre.strip()
            ]

            games.append({
                "id": row.get("id_game"),
                "title": row.get("nama_game"),
                "genre": genres[0] if genres else "",
                "genres": genres,
                "tags": genres,
                "dev": row.get("developer"),
                "pub": row.get("publisher"),
                "price": row.get("harga_sekarang") or 0,
                "rating": rating,
                "img": row.get("url_gambar") or None,
                "ac": "#39d353",
                "release_date": str(row.get("tanggal_rilis") or "-"),
                "description": row.get("deskripsi") or "",
                "good_review": good,
                "bad_review": bad,
                "total_reviews": total,
                "current_player": int(row.get("current_player") or 0),
                "peak_player": int(row.get("peak_player") or 0),
            })

        return games

    except Exception as e:
        print("ERROR popular_logic:", e)
        return []


def sort_games(games: list, order: str = "desc") -> list:
    """Sort list game yang sudah ada di memori tanpa query ulang."""
    return sorted(
        games,
        key=lambda game: game.get("peak_player", 0),
        reverse=(order.lower() == "desc"),
    )


def _similarity(a: str, b: str) -> float:
    """Hitung tingkat kemiripan dua string."""
    return SequenceMatcher(None, a, b).ratio()


def _build_searchable_text(game: dict) -> str:
    """Gabungkan field game yang bisa dicari."""
    title = game.get("title") or ""
    dev = game.get("dev") or ""
    pub = game.get("pub") or ""
    genres = " ".join(game.get("genres", []) or [])
    tags = " ".join(game.get("tags", []) or [])

    return f"{title} {dev} {pub} {genres} {tags}".lower()


def search_games(games: list, query: str) -> list:
    """
    Filter game berdasarkan title, developer, publisher, genre, dan tags.

    Mendukung:
    - exact substring search
    - multi-keyword search
    - fuzzy search sederhana untuk typo ringan
    """
    query = (query or "").strip().lower()

    if not query:
        return games

    keywords = query.split()
    filtered = []

    for game in games:
        searchable_text = _build_searchable_text(game)
        searchable_words = searchable_text.split()

        exact_match = all(
            keyword in searchable_text
            for keyword in keywords
        )

        fuzzy_match = all(
            any(
                keyword in word or _similarity(keyword, word) >= FUZZY_THRESHOLD
                for word in searchable_words
            )
            for keyword in keywords
        )

        if exact_match or fuzzy_match:
            filtered.append(game)

    return filtered