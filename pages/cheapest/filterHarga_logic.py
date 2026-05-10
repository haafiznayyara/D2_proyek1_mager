"""
filterHarga_logic.py
────────────────────
Logic untuk filter game berdasarkan harga.
"""

from database.connection import connection_database


def get_games_by_price(min_price=0, max_price=None):
    """
    Ambil game dari database yang harganya dalam range min_price - max_price.
    
    Args:
        min_price: Harga minimum (default: 0)
        max_price: Harga maximum (default: None = tidak terbatas)
    
    Returns:
        list: List game yang memenuhi kriteria harga
    """
    try:
        conn = connection_database()
        cursor = conn.cursor()

        # Query dengan JOIN ke detail_genre dan genre
        if max_price is None:
            # Hanya filter minimum
            query = """
                SELECT g.*,
                       GROUP_CONCAT(gr.nama_genre SEPARATOR '||') AS genres_str
                FROM game g
                LEFT JOIN detail_genre dg ON g.id_game = dg.id_game
                LEFT JOIN genre gr        ON dg.id_genre = gr.id_genre
                WHERE g.harga_sekarang >= %s
                GROUP BY g.id_game
                ORDER BY g.harga_sekarang ASC
            """
            cursor.execute(query, (min_price,))
        else:
            # Filter range min-max
            query = """
                SELECT g.*,
                       GROUP_CONCAT(gr.nama_genre SEPARATOR '||') AS genres_str
                FROM game g
                LEFT JOIN detail_genre dg ON g.id_game = dg.id_game
                LEFT JOIN genre gr        ON dg.id_genre = gr.id_genre
                WHERE g.harga_sekarang >= %s AND g.harga_sekarang <= %s
                GROUP BY g.id_game
                ORDER BY g.harga_sekarang ASC
            """
            cursor.execute(query, (min_price, max_price))

        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        games = []
        for row in rows:
            good = int(row.get("good_review") or 0)
            bad = int(row.get("bad_review") or 0)
            total = good + bad
            rating = round(good / total * 100) if total > 0 else 0

            # Parse genres dari GROUP_CONCAT
            genres_str = row.get("genres_str") or ""
            genres = [g.strip() for g in genres_str.split("||") if g.strip()]

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
        print("ERROR filterHarga_logic:", e)
        return []


def filter_games_by_price(games, min_price=0, max_price=None):
    """
    Filter list game yang sudah ada di memori berdasarkan harga.
    Fungsi ini digunakan ketika data sudah di-load sebelumnya.
    
    Args:
        games: List game yang akan difilter
        min_price: Harga minimum
        max_price: Harga maximum (None = tidak terbatas)
    
    Returns:
        list: List game yang memenuhi kriteria
    """
    if max_price is None:
        return [g for g in games if g["price"] >= min_price]
    else:
        return [
            g for g in games
            if min_price <= g["price"] <= max_price
        ]


def search_games(games, query):
    """
    Filter game berdasarkan query pencarian.
    
    Args:
        games: List game
        query: String pencarian
    
    Returns:
        list: Game yang cocok dengan query
    """
    q = query.strip().lower()
    if not q:
        return games
    
    return [
        g for g in games
        if q in g["title"].lower()
        or q in (g["dev"] or "").lower()
        or any(q in tag.lower() for tag in g.get("tags", []))
    ]


def parse_price_input(price_str):
    """
    Parse input harga dari string.
    Menghilangkan "Rp", titik, koma, dan spasi.
    
    Args:
        price_str: String input harga (contoh: "Rp 50.000", "50000", "50,000")
    
    Returns:
        int atau None: Nilai harga dalam bentuk integer, atau None jika invalid
    """
    if not price_str or price_str.strip() == "":
        return None
    
    # Hilangkan "Rp", spasi, titik, koma
    cleaned = price_str.replace("Rp", "").replace(".", "").replace(",", "").replace(" ", "").strip()
    
    try:
        return int(cleaned)
    except ValueError:
        return None


def fmt_price(price):
    """Format harga ke format Rupiah."""
    if price == 0:
        return "Gratis"
    return "Rp {:,}".format(int(price)).replace(",", ".")
