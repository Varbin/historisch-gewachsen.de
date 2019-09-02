import sqlite3


def update_table(conn, table, quotefile):
    conn.execute(f"DROP TABLE IF EXISTS {table};")
    conn.execute(f"CREATE TABLE IF NOT EXISTS {table} (quote varchar UNIQUE);")
    conn.commit()

    with open(quotefile) as quotes:
        for quote in quotes.readlines():
            quote = quote.strip()
            try:
                conn.execute(f"INSERT INTO {table} VALUES (?);", (quote,))
            except sqlite3.IntegrityError:
                conn.rollback()
            else:
                conn.commit()

    conn.commit()


if __name__ == "__main__":
    conn = sqlite3.connect("quotes.sqlite")

    conn.execute("CREATE TABLE IF NOT EXISTS suggestions (suggestion varchar, sugesttion_time date);")
    conn.commit()

    update_table(conn, "quotes_de", "quotes_de.txt")
    update_table(conn, "quotes_en", "quotes_en.txt")

