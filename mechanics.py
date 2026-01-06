from flask import Blueprint, request, redirect
from markupsafe import escape

from db import get_conn
from ui import render_page, table

bp = Blueprint("mechanics", __name__)


@bp.route("/mechanics")
def mechanics():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT MechanicID, MechanicName, Expertise FROM Mechanic ORDER BY MechanicID ASC")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    actions = """
    <div class="card">
      <div class="actions">
        <a class="btn primary" href="/add-mechanic">+ Add Mechanic</a>
      </div>
    </div>
    """

    def row_html(r):
        mid, name, exp = r
        return (
            f"<tr>"
            f"<td>{mid}</td>"
            f"<td>{escape(name)}</td>"
            f"<td>{escape(exp or '')}</td>"
            f"<td><a class='btn' href='/edit-mechanic/{mid}'>Edit</a></td>"
            f"</tr>"
        )

    t = table(["ID", "Name", "Expertise", "Action"], rows, row_html)
    return render_page("Mechanics", "/mechanics", actions + t, "Staff and their expertise")


@bp.route("/add-mechanic", methods=["GET", "POST"])
def add_mechanic():
    if request.method == "POST":
        name = request.form["name"].strip()
        expertise = request.form.get("expertise", "").strip()

        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO Mechanic (MechanicName, Expertise) VALUES (%s, %s)",
            (name, expertise if expertise else None)
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect("/mechanics")

    body = """
    <div class="card">
      <form method="post">
        <div class="field"><label>Mechanic Name</label><input name="name" required></div>
        <div class="field"><label>Expertise</label><input name="expertise"></div>
        <div class="actions">
          <button class="btn primary" type="submit">Save</button>
          <a class="btn" href="/mechanics">Cancel</a>
        </div>
      </form>
    </div>
    """
    return render_page("Add Mechanic", "/mechanics", body)


@bp.route("/edit-mechanic/<int:mechanic_id>", methods=["GET", "POST"])
def edit_mechanic(mechanic_id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT MechanicName, Expertise FROM Mechanic WHERE MechanicID=%s", (mechanic_id,))
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        return redirect("/mechanics")

    if request.method == "POST":
        name = request.form["name"].strip()
        expertise = request.form.get("expertise", "").strip()
        cur.execute(
            "UPDATE Mechanic SET MechanicName=%s, Expertise=%s WHERE MechanicID=%s",
            (name, expertise if expertise else None, mechanic_id)
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect("/mechanics")

    name, exp = row
    cur.close()
    conn.close()

    body = f"""
    <div class="card">
      <form method="post">
        <div class="field"><label>Mechanic Name</label><input name="name" value="{escape(name)}" required></div>
        <div class="field"><label>Expertise</label><input name="expertise" value="{escape(exp or '')}"></div>
        <div class="actions">
          <button class="btn primary" type="submit">Update</button>
          <a class="btn" href="/mechanics">Cancel</a>
        </div>
      </form>
    </div>
    """
    return render_page("Edit Mechanic", "/mechanics", body)
