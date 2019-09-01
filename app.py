#!/usr/bin/env python3

import os
import secrets
import sqlite3

from flask import Flask
from flask import Response
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

app = Flask(__name__)
app.config["API_URL"] = os.environ.get("API_URL", "http://localhost:5000/api/getQuote/")
app.config["DATABASE"] = "quotes.sqlite"


def get_quote(lang):
    """Return a quote in lang."""
    with sqlite3.connect(app.config["DATABASE"]) as db:
        return db.execute(f"SELECT quote FROM quotes_{lang} ORDER BY random() LIMIT 1").fetchone()[0]


@app.route("/")
@app.route("/<lang>/")
def index(lang=None):
    if lang is None:
        lang = request.accept_languages.best_match(['en', 'de'])
    elif lang not in ("de", "en"):
        return redirect(url_for("index", lang="en"))

    nonce = secrets.token_hex(32)

    response = Response(
        render_template("index.html", lang=lang, nonce=nonce, quote=get_quote(lang))
    )
    response.headers["Content-Security-Policy"] = f"default-src 'self'; script-src 'nonce-{nonce}'"

    return response


@app.route("/<lang>/suggest/", methods=["GET", "POST"])
def suggest(lang):
    if lang not in ("de", "en"):
        return redirect(url_for("suggest", lang="en"))

    if request.method == "POST":
        reason = request.form.get("reason")
        thanks = None
        if reason:
            thanks = "yes"

            with sqlite3.connect(app.config["DATABASE"]) as conn:
                conn.execute("INSERT INTO suggestions VALUES (?, CURRENT_TIMESTAMP);", (reason,))

        return redirect(url_for("suggest", lang=lang, thanks=thanks))

    return render_template("suggest.html", lang=lang, thanks=bool(request.args.get("thanks")))


@app.route("/<lang>/api/getQuote/")
def api(lang):
    if lang not in ("de", "en"):
        return Response(
            jsonify({"status": "error", "message": "Unknown language!"}),
            content_type="text/json",
            status=400,
        )

    table = {"de": "quotes_de", "en": "quotes_en"}[lang]
    quote = get_quote(lang)
    return jsonify(
        {"status": "ok", "quote": quote}
    )
