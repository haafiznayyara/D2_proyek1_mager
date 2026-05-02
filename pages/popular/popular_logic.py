# popular_logic.py
from database.connection import connection_database


def get_popular_games(order: str = "desc") -> list:
    """
    Ambil game dari DB diurutkan berdasarkan peak_player.
    order: "desc" → tertinggi dulu, "asc" → terendah dulu
    """
    direction = "DESC" if order.lower() == "desc" else "ASC"

    try:
        conn   = connection_database()
        cursor = conn.cursor()

        cursor.execute(f"""
            SELECT g.*,
                   GROUP_CONCAT(gr.nama_genre SEPARATOR '||') AS genres_str
            FROM game g
            LEFT JOIN detail_genre dg ON g.id_game = dg.id_game
            LEFT JOIN genre gr        ON dg.id_genre = gr.id_genre
            GROUP BY g.id_game
            ORDER BY g.peak_player {direction}
        """)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        games = []
        for row in rows:
            good  = int(row.get("good_review") or 0)
            bad   = int(row.get("bad_review")  or 0)
            total = good + bad
            rating = round(good / total * 100) if total > 0 else 0

            # Parse genres dari GROUP_CONCAT
            genres_str = row.get("genres_str") or ""
            genres = [g.strip() for g in genres_str.split("||") if g.strip()]

            games.append({
                "id":             row.get("id_game"),
                "title":          row.get("nama_game"),
                "genre":          genres[0] if genres else "",
                "genres":         genres,
                "tags":           genres,
                "dev":            row.get("developer"),
                "pub":            row.get("publisher"),
                "price":          row.get("harga_sekarang") or 0,
                "rating":         rating,
                "img":            row.get("url_gambar") or None,
                "ac":             "#39d353",
                "release_date":   str(row.get("tanggal_rilis") or "-"),
                "description":    row.get("deskripsi") or "",
                "good_review":    good,
                "bad_review":     bad,
                "total_reviews":  total,
                "current_player": int(row.get("current_player") or 0),
                "peak_player":    int(row.get("peak_player")    or 0),
            })
        return games

    except Exception as e:
        print("ERROR popular_logic:", e)
        return []


def sort_games(games: list, order: str = "desc") -> list:
    """Sort list game yang sudah ada di memori tanpa query ulang."""
    return sorted(
        games,
        key=lambda g: g["peak_player"],
        reverse=(order.lower() == "desc"),
    )


def search_games(games: list, query: str) -> list:
    """Filter game berdasarkan judul, developer, atau genre."""
    q = query.strip().lower()
    if not q:
        return games
    return [
        g for g in games
        if q in g["title"].lower()
        or q in (g["dev"] or "").lower()
        or any(q in tag.lower() for tag in g.get("tags", []))
    ]