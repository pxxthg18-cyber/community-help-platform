import os
import sqlite3
from pathlib import Path
from flask import Flask, abort, flash, g, redirect, render_template, request, url_for

BASE_DIR = Path(__file__).resolve().parent
CATEGORIES = ("Education", "Food", "Transportation", "Emergency Assistance")
STATUSES = ("Open", "Accepted", "Completed")

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "local-development-key-change-me")
app.config["DATABASE"] = os.environ.get("DATABASE_PATH", str(BASE_DIR / "community_help.db"))


def get_db():
    if "db" not in g:
        db_path = Path(app.config["DATABASE"])
        db_path.parent.mkdir(parents=True, exist_ok=True)
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    get_db().executescript("""
        CREATE TABLE IF NOT EXISTS help_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            location TEXT NOT NULL,
            requester TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Open'
                CHECK (status IN ('Open', 'Accepted', 'Completed')),
            volunteer TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)
    get_db().commit()


@app.before_request
def ensure_database():
    init_db()


@app.get("/")
def index():
    db = get_db()
    totals = {
        "all": db.execute("SELECT COUNT(*) FROM help_requests").fetchone()[0],
        "open": db.execute("SELECT COUNT(*) FROM help_requests WHERE status = 'Open'").fetchone()[0],
        "completed": db.execute("SELECT COUNT(*) FROM help_requests WHERE status = 'Completed'").fetchone()[0],
    }
    recent = db.execute(
        "SELECT * FROM help_requests ORDER BY created_at DESC, id DESC LIMIT 5"
    ).fetchall()
    return render_template("index.html", totals=totals, recent=recent)


@app.get("/requests")
def list_requests():
    category = request.args.get("category", "").strip()
    status = request.args.get("status", "").strip()
    if category and category not in CATEGORIES:
        category = ""
    if status and status not in STATUSES:
        status = ""
    sql = "SELECT * FROM help_requests WHERE 1=1"
    params = []
    if category:
        sql += " AND category = ?"
        params.append(category)
    if status:
        sql += " AND status = ?"
        params.append(status)
    sql += " ORDER BY created_at DESC, id DESC"
    rows = get_db().execute(sql, params).fetchall()
    return render_template("requests.html", requests=rows, categories=CATEGORIES,
                           statuses=STATUSES, selected_category=category,
                           selected_status=status)


@app.route("/request-help", methods=["GET", "POST"])
def request_help():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "").strip()
        location = request.form.get("location", "").strip()
        requester = request.form.get("requester", "").strip()
        errors = []
        if not title or len(title) > 100:
            errors.append("Title is required and must be 100 characters or fewer.")
        if not description or len(description) > 1000:
            errors.append("Description is required and must be 1000 characters or fewer.")
        if category not in CATEGORIES:
            errors.append("Choose a valid category.")
        if not location or len(location) > 120:
            errors.append("Location is required and must be 120 characters or fewer.")
        if not requester or len(requester) > 80:
            errors.append("Your display name is required and must be 80 characters or fewer.")
        if errors:
            for error in errors:
                flash(error, "error")
            return render_template("request_help.html", categories=CATEGORIES, form=request.form), 400
        get_db().execute(
            """INSERT INTO help_requests (title, description, category, location, requester)
               VALUES (?, ?, ?, ?, ?)""",
            (title, description, category, location, requester),
        )
        get_db().commit()
        flash("Your help request was submitted.", "success")
        return redirect(url_for("list_requests"))
    return render_template("request_help.html", categories=CATEGORIES, form={})


@app.post("/requests/<int:request_id>/accept")
def accept_request(request_id):
    volunteer = request.form.get("volunteer", "").strip()
    if not volunteer or len(volunteer) > 80:
        flash("Enter a display name (80 characters or fewer) to volunteer.", "error")
        return redirect(url_for("list_requests")), 400
    db = get_db()
    cursor = db.execute(
        "UPDATE help_requests SET status = 'Accepted', volunteer = ? WHERE id = ? AND status = 'Open'",
        (volunteer, request_id),
    )
    db.commit()
    if cursor.rowcount == 0:
        exists = db.execute("SELECT id FROM help_requests WHERE id = ?", (request_id,)).fetchone()
        if exists is None:
            abort(404)
        flash("This request is no longer open and cannot be accepted.", "error")
    else:
        flash("Thank you for offering to help!", "success")
    return redirect(url_for("list_requests"))


@app.post("/requests/<int:request_id>/complete")
def complete_request(request_id):
    db = get_db()
    cursor = db.execute(
        "UPDATE help_requests SET status = 'Completed' WHERE id = ? AND status = 'Accepted'",
        (request_id,),
    )
    db.commit()
    if cursor.rowcount == 0:
        exists = db.execute("SELECT id FROM help_requests WHERE id = ?", (request_id,)).fetchone()
        if exists is None:
            abort(404)
        flash("Only accepted requests can be marked completed.", "error")
    else:
        flash("Request marked as completed.", "success")
    return redirect(url_for("list_requests"))


@app.get("/health")
def health():
    get_db().execute("SELECT 1").fetchone()
    return {"status": "ok", "service": "community-help-platform"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)
