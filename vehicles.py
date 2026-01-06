from flask import Blueprint, request, redirect
from markupsafe import escape

from db import get_conn
from ui import render_page, table

bp = Blueprint("vehicles", __name__)


@bp.route("/vehicles")
def vehicles():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT v.VehicleID, c.CustomerName, v.VehicleModel, v.RegistrationNumber, v.ManufacturingYear
        FROM Vehicle v
        JOIN Customer c ON v.CustomerID = c.CustomerID
        ORDER BY v.VehicleID ASC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    actions = """
    <div class="card">
      <div class="actions">
        <a class="btn primary" href="/add-vehicle">+ Add Vehicle</a>
      </div>
    </div>
    """

    def row_html(r):
        vid, cname, model, reg, year = r
        return (
            f"<tr>"
            f"<td>{vid}</td>"
            f"<td>{escape(cname)}</td>"
            f"<td>{escape(model or '')}</td>"
            f"<td>{escape(reg or '')}</td>"
            f"<td>{escape(str(year or ''))}</td>"
            f"<td><a class='btn' href='/edit-vehicle/{vid}'>Edit</a></td>"
            f"</tr>"
        )

    t = table(["ID", "Customer", "Model", "Registration", "Year", "Action"], rows, row_html)
    return render_page("Vehicles", "/vehicles", actions + t, "Vehicles linked to customers")


@bp.route("/add-vehicle", methods=["GET", "POST"])
def add_vehicle():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT CustomerID, CustomerName FROM Customer ORDER BY CustomerName ASC")
    customers_ = cur.fetchall()

    if request.method == "POST":
        customer_id = request.form["customer_id"]
        model = request.form.get("model", "").strip()
        reg = request.form.get("reg", "").strip()
        year = request.form.get("year", "").strip()
        year_val = int(year) if year else None

        cur.execute(
            """INSERT INTO Vehicle (CustomerID, VehicleModel, RegistrationNumber, ManufacturingYear)
               VALUES (%s, %s, %s, %s)""",
            (customer_id, model if model else None, reg if reg else None, year_val)
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect("/vehicles")

    options = "".join([f'<option value="{c[0]}">{escape(c[1])}</option>' for c in customers_])
    cur.close()
    conn.close()

    body = f"""
    <div class="card">
      <form method="post">
        <div class="field"><label>Customer</label><select name="customer_id" required>{options}</select></div>
        <div class="field"><label>Vehicle Model</label><input name="model"></div>
        <div class="field"><label>Registration Number</label><input name="reg"></div>
        <div class="field"><label>Manufacturing Year</label><input name="year" type="number"></div>
        <div class="actions">
          <button class="btn primary" type="submit">Save</button>
          <a class="btn" href="/vehicles">Cancel</a>
        </div>
      </form>
    </div>
    """
    return render_page("Add Vehicle", "/vehicles", body)


@bp.route("/edit-vehicle/<int:vehicle_id>", methods=["GET", "POST"])
def edit_vehicle(vehicle_id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT VehicleID, CustomerID, VehicleModel, RegistrationNumber, ManufacturingYear FROM Vehicle WHERE VehicleID=%s", (vehicle_id,))
    v = cur.fetchone()
    if not v:
        cur.close()
        conn.close()
        return redirect("/vehicles")

    cur.execute("SELECT CustomerID, CustomerName FROM Customer ORDER BY CustomerName ASC")
    customers_ = cur.fetchall()

    if request.method == "POST":
        customer_id = request.form["customer_id"]
        model = request.form.get("model", "").strip()
        reg = request.form.get("reg", "").strip()
        year = request.form.get("year", "").strip()
        year_val = int(year) if year else None

        cur.execute("""
            UPDATE Vehicle
            SET CustomerID=%s, VehicleModel=%s, RegistrationNumber=%s, ManufacturingYear=%s
            WHERE VehicleID=%s
        """, (customer_id, model if model else None, reg if reg else None, year_val, vehicle_id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect("/vehicles")

    _, cust_id, model, reg, year = v
    options = "".join([
        f'<option value="{c[0]}" {"selected" if c[0]==cust_id else ""}>{escape(c[1])}</option>'
        for c in customers_
    ])
    cur.close()
    conn.close()

    body = f"""
    <div class="card">
      <form method="post">
        <div class="field"><label>Customer</label><select name="customer_id" required>{options}</select></div>
        <div class="field"><label>Vehicle Model</label><input name="model" value="{escape(model or '')}"></div>
        <div class="field"><label>Registration Number</label><input name="reg" value="{escape(reg or '')}"></div>
        <div class="field"><label>Manufacturing Year</label><input name="year" type="number" value="{escape(str(year or ''))}"></div>
        <div class="actions">
          <button class="btn primary" type="submit">Update</button>
          <a class="btn" href="/vehicles">Cancel</a>
        </div>
      </form>
    </div>
    """
    return render_page("Edit Vehicle", "/vehicles", body)
