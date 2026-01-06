from flask import Blueprint, request, redirect
from markupsafe import escape

from db import get_conn
from ui import render_page, table

bp = Blueprint("services", __name__)


@bp.route("/services")
def services():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT ServiceID, ServiceName, Cost FROM Service ORDER BY ServiceID ASC")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    actions = """
    <div class="card">
      <div class="actions">
        <a class="btn primary" href="/add-service">+ Add Service</a>
      </div>
    </div>
    """

    def row_html(r):
        sid, sname, cost = r
        return (
            f"<tr>"
            f"<td>{sid}</td>"
            f"<td>{escape(sname)}</td>"
            f"<td>{escape(str(cost))}</td>"
            f"<td><a class='btn' href='/edit-service/{sid}'>Edit</a></td>"
            f"</tr>"
        )

    t = table(["ID", "Service", "Cost", "Action"], rows, row_html)
    return render_page("Services", "/services", actions + t, "Service catalog and pricing")


@bp.route("/add-service", methods=["GET", "POST"])
def add_service():
    if request.method == "POST":
        name = request.form["name"].strip()
        cost = request.form["cost"].strip()

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("INSERT INTO Service (ServiceName, Cost) VALUES (%s, %s)", (name, cost))
        conn.commit()
        cur.close()
        conn.close()
        return redirect("/services")

    body = """
    <div class="card">
      <form method="post">
        <div class="field"><label>Service Name</label><input name="name" required></div>
        <div class="field"><label>Cost</label><input name="cost" type="number" step="0.01" required></div>
        <div class="actions">
          <button class="btn primary" type="submit">Save</button>
          <a class="btn" href="/services">Cancel</a>
        </div>
      </form>
    </div>
    """
    return render_page("Add Service", "/services", body)


@bp.route("/edit-service/<int:service_id>", methods=["GET", "POST"])
def edit_service(service_id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT ServiceName, Cost FROM Service WHERE ServiceID=%s", (service_id,))
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        return redirect("/services")

    if request.method == "POST":
        name = request.form["name"].strip()
        cost = request.form["cost"].strip()
        cur.execute("UPDATE Service SET ServiceName=%s, Cost=%s WHERE ServiceID=%s", (name, cost, service_id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect("/services")

    name, cost = row
    cur.close()
    conn.close()

    body = f"""
    <div class="card">
      <form method="post">
        <div class="field"><label>Service Name</label><input name="name" value="{escape(name)}" required></div>
        <div class="field"><label>Cost</label><input name="cost" type="number" step="0.01" value="{escape(str(cost))}" required></div>
        <div class="actions">
          <button class="btn primary" type="submit">Update</button>
          <a class="btn" href="/services">Cancel</a>
        </div>
      </form>
    </div>
    """
    return render_page("Edit Service", "/services", body)
