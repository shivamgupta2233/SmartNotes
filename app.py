from flask import (
    Flask,
    render_template,
    request,
    redirect,
    flash,
    Response,
    send_file
)

import csv
from io import StringIO
from reportlab.pdfgen import canvas

from config import Config
from database import db
from models import Note

app = Flask(__name__)

app.secret_key = "smartnotes123"

app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    db.create_all()


# ----------------------------------
# HOME
# ----------------------------------

@app.route("/")
def home():

    search = request.args.get("search", "")

    category = request.args.get("category", "All")

    query = Note.query

    # Search
    if search:

        query = query.filter(

            (Note.title.contains(search)) |

            (Note.content.contains(search))

        )

    # Category
    if category != "All":

        query = query.filter(

            Note.category == category

        )

    notes = query.order_by(

        Note.pinned.desc(),

        Note.created.desc()

    ).all()

    favorites = Note.query.filter_by(
        favorite=True
    ).count()

    pinned = Note.query.filter_by(
        pinned=True
    ).count()

    categories = db.session.query(
        Note.category
    ).distinct().count()

    return render_template(

        "index.html",

        notes=notes,

        search=search,

        category=category,

        favorites=favorites,

        pinned=pinned,

        categories=categories

    )
    
# ----------------------------------
# ADD NOTE
# ----------------------------------

@app.route("/add", methods=["POST"])
def add():

    note = Note(
        title=request.form["title"],
        category=request.form["category"],
        content=request.form["content"]
    )

    db.session.add(note)
    db.session.commit()

    flash("✅ Note Added Successfully!", "success")

    return redirect("/")

# ----------------------------------
# DELETE NOTE
# ----------------------------------

@app.route("/delete/<int:id>")
def delete(id):

    note = Note.query.get_or_404(id)

    db.session.delete(note)

    db.session.commit()

    flash("🗑 Note Deleted Successfully!", "danger")

    return redirect("/")

# ----------------------------------
# EDIT NOTE
# ----------------------------------

@app.route("/edit/<int:id>")
def edit(id):

    note = Note.query.get_or_404(id)

    search = ""

    category = "All"

    notes = Note.query.order_by(
        Note.pinned.desc(),
        Note.created.desc()
    ).all()

    favorites = Note.query.filter_by(
        favorite=True
    ).count()

    pinned = Note.query.filter_by(
        pinned=True
    ).count()

    categories = db.session.query(
        Note.category
    ).distinct().count()

    return render_template(
        "index.html",
        note=note,
        notes=notes,
        search=search,
        category=category,
        favorites=favorites,
        pinned=pinned,
        categories=categories
    )
    
# ----------------------------------
# UPDATE NOTE
# ----------------------------------

@app.route("/update/<int:id>", methods=["POST"])
def update(id):

    note = Note.query.get_or_404(id)

    note.title = request.form["title"]
    note.category = request.form["category"]
    note.content = request.form["content"]

    db.session.commit()

    flash("✏️ Note Updated Successfully!", "info")

    return redirect("/")

# ----------------------------------
# FAVORITE NOTE
# ----------------------------------

@app.route("/favorite/<int:id>")
def favorite(id):

    note = Note.query.get_or_404(id)

    note.favorite = not note.favorite

    db.session.commit()

    return redirect("/")

# ----------------------------------
# PIN NOTE
# ----------------------------------

@app.route("/pin/<int:id>")
def pin(id):

    note = Note.query.get_or_404(id)

    note.pinned = not note.pinned

    db.session.commit()

    return redirect("/")

# ----------------------------------
# EXPORT PDF
# ----------------------------------

@app.route("/export/pdf")
def export_pdf():

    notes = Note.query.order_by(
        Note.pinned.desc(),
        Note.created.desc()
    ).all()

    pdf_path = "SmartNotes.pdf"

    c = canvas.Canvas(pdf_path)

    y = 800

    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, y, "Smart Notes")
    y -= 40

    c.setFont("Helvetica", 11)

    for note in notes:

        c.drawString(40, y, f"Title : {note.title}")
        y -= 20

        c.drawString(40, y, f"Category : {note.category}")
        y -= 20

        c.drawString(40, y, f"Content : {note.content[:90]}")
        y -= 35

        if y < 60:
            c.showPage()
            y = 800

    c.save()

    return send_file(
        pdf_path,
        as_attachment=True
    )
    
# ----------------------------------
# EXPORT CSV
# ----------------------------------

@app.route("/export/csv")
def export_csv():

    notes = Note.query.order_by(
        Note.created.desc()
    ).all()

    output = StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "Title",
        "Category",
        "Favorite",
        "Pinned",
        "Created",
        "Content"
    ])

    for note in notes:

        writer.writerow([
            note.title,
            note.category,
            "Yes" if note.favorite else "No",
            "Yes" if note.pinned else "No",
            note.created.strftime("%d-%m-%Y %H:%M"),
            note.content
        ])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=SmartNotes.csv"
        }
    )
    
# ----------------------------------
# MAIN
# ----------------------------------

if __name__ == "__main__":

    app.run(
        debug=True,
        use_reloader=False,
        port=5001
    )                