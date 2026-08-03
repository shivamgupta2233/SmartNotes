import os
from werkzeug.utils import secure_filename
from auth import auth
from flask_login import LoginManager, login_required, current_user
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
from models import Note, User

app = Flask(__name__)
UPLOAD_FOLDER = "static/uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

app.secret_key = "smartnotes123"

app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = "auth.login"

login_manager.login_message = "Please login to continue."

login_manager.login_message_category = "warning"
app.register_blueprint(auth)
with app.app_context():
    db.create_all()
    
    @login_manager.user_loader
    def load_user(user_id):  

        return User.query.get(int(user_id))

# ----------------------------------
# HOME
# ----------------------------------

@app.route("/")
@login_required
def home():

    search = request.args.get("search")

    category = request.args.get("category", "All")

    query = Note.query.filter_by(
        user_id=current_user.id
    )

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
@login_required
def add():

    title = request.form["title"]
    category = request.form["category"]
    content = request.form["content"]

    image = request.files.get("image")

    filename = None

    if image and image.filename != "":

        filename = secure_filename(image.filename)

        image.save(
            os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )
        )

    note = Note(
        title=title,
        category=category,
        content=content,
        user_id=current_user.id,
        image=filename
    )

    db.session.add(note)
    db.session.commit()

    flash("✅ Note Added Successfully!", "success")

    return redirect("/")
# ----------------------------------
# DELETE NOTE
# ----------------------------------


@app.route("/delete/<int:id>")
@login_required
def delete(id):

    note = Note.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()
    if note.image:

        image_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        note.image
    )

    if os.path.exists(image_path):
        os.remove(image_path)

    db.session.delete(note)
    db.session.commit()

    flash("🗑 Note Deleted Successfully!", "danger")

    return redirect("/")

# ----------------------------------
# EDIT NOTE
# ----------------------------------

@app.route("/edit/<int:id>")
def edit(id):

    note = Note.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

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
@login_required
def update(id):

    note = Note.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    note.title = request.form["title"]
    note.category = request.form["category"]
    note.content = request.form["content"]

    image = request.files.get("image")
    print("FILES:", request.files)
    print("IMAGE:", image)
    print("FILENAME:", image.filename if image else "No Image")

    if image and image.filename != "":

        # Delete old image
        if note.image:

            old_path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                note.image
            )

            if os.path.exists(old_path):
                os.remove(old_path)

        # Save new image
        filename = secure_filename(image.filename)

        image.save(
            os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )
        )

        note.image = filename

    db.session.commit()

    flash("✏️ Note Updated Successfully!", "info")

    return redirect("/")

# ----------------------------------
# FAVORITE NOTE
# ----------------------------------

@app.route("/favorite/<int:id>")
def favorite(id):

    note = Note.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    note.favorite = not note.favorite

    db.session.commit()

    return redirect("/")

# ----------------------------------
# PIN NOTE
# ----------------------------------

@app.route("/pin/<int:id>")
def pin(id):

    note = Note.query.filter_by(
    id=id,
    user_id=current_user.id
).first_or_404()
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