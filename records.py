from flask import Blueprint, request, redirect
from markupsafe import escape
from db import get_conn
from ui import render_page, table

bp = Blueprint("records", __name__)

# -------------------- RECORDS LIST --------------------
@bp.route("/records")
def records():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT sr.RecordID,
               v.RegistrationNumber,
               s.ServiceName,
               m.MechanicName,
               sr.ServiceDate,
               sr.Status
        FROM Service_Record sr
        JOIN Vehicle v ON sr.VehicleID = v.VehicleID
        JOIN Service s ON sr.ServiceID = s.ServiceID
        JOIN Mechanic m ON sr.MechanicID = m.MechanicID
        ORDER BY sr.RecordID ASC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    actions = """
    <div class="card">
      <div class="actions">
        <a class="btn primary" href="/add-record">+ Add Record</a>
      </div>
    </div>
    """

    def row_html(r):
        rid, reg, sname, mname, datev, status = r
        return (
            f"<tr>"
            f"<td>{rid}</td>"
            f"<td>{escape(reg or '')}</td>"
            f"<td>{escape(sname)}</td>"
            f"<td>{escape(mname)}</td>"
            f"<td>{escape(str(datev))}</td>"
            f"<td>{escape(status)}</td>"
            f"<td><a class='btn' href='/edit-record/{rid}'>Edit</a></td>"
            f"</tr>"
        )

    t = table(["Record ID", "Vehicle Reg", "Service", "Mechanic", "Date", "Status", "Action"], rows, row_html)
    return render_page("Service Records", "/records", actions + t, "Track jobs: vehicle + service + mechanic + status")

# -------------------- ADD RECORD --------------------
@bp.route("/add-record", methods=["GET", "POST"])
def add_record():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT VehicleID, RegistrationNumber FROM Vehicle ORDER BY RegistrationNumber ASC")
    vehicles_ = cur.fetchall()
    cur.execute("SELECT ServiceID, ServiceName FROM Service ORDER BY ServiceName ASC")
    services_ = cur.fetchall()
    cur.execute("SELECT MechanicID, MechanicName FROM Mechanic ORDER BY MechanicName ASC")
    mechanics_ = cur.fetchall()

    if request.method == "POST":
        vehicle_id = request.form["vehicle_id"]
        service_id = request.form["service_id"]
        mechanic_id = request.form["mechanic_id"]
        service_date = request.form["service_date"]
        status = request.form["status"]

        cur.execute(
            """INSERT INTO Service_Record (VehicleID, ServiceID, MechanicID, ServiceDate, Status)
               VALUES (%s, %s, %s, %s, %s)""",
            (vehicle_id, service_id, mechanic_id, service_date, status)
        )
        conn.commit()

        # Reset the AUTO_INCREMENT after adding a new record
        cur.execute("SELECT COUNT(*) FROM Service_Record")
        total_records = cur.fetchone()[0]
        
        if total_records == 1:  # If it's the first record after deletion
            cur.execute("ALTER TABLE Service_Record AUTO_INCREMENT = 1")
        else:
            cur.execute("SELECT MAX(RecordID) FROM Service_Record")
            max_id = cur.fetchone()[0]
            cur.execute(f"ALTER TABLE Service_Record AUTO_INCREMENT = {max_id + 1}")

        conn.commit()
        cur.close()
        conn.close()
        return redirect("/records")

    v_opts = "".join([f'<option value="{v[0]}">{escape(v[1] or "")}</option>' for v in vehicles_])
    s_opts = "".join([f'<option value="{s[0]}">{escape(s[1])}</option>' for s in services_])
    m_opts = "".join([f'<option value="{m[0]}">{escape(m[1])}</option>' for m in mechanics_])

    cur.close()
    conn.close()

    body = f"""
    <div class="card">
      <form method="post">
        <div class="field"><label>Vehicle</label><select name="vehicle_id" required>{v_opts}</select></div>
        <div class="field"><label>Service</label><select name="service_id" required>{s_opts}</select></div>
        <div class="field"><label>Mechanic</label><select name="mechanic_id" required>{m_opts}</select></div>
        <div class="field"><label>Service Date</label><input type="date" name="service_date" required></div>
        <div class="field">
          <label>Status</label>
          <select name="status">
            <option>Pending</option>
            <option>In Progress</option>
            <option>Completed</option>
          </select>
        </div>
        <div class="actions">
          <button class="btn primary" type="submit">Save</button>
          <a class="btn" href="/records">Cancel</a>
        </div>
      </form>
    </div>
    """
    return render_page("Add Service Record", "/records", body)

# -------------------- EDIT RECORD --------------------
@bp.route("/edit-record/<int:record_id>", methods=["GET", "POST"])
def edit_record(record_id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT VehicleID, ServiceID, MechanicID, ServiceDate, Status FROM Service_Record WHERE RecordID=%s", (record_id,))
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        return redirect("/records")

    cur.execute("SELECT VehicleID, RegistrationNumber FROM Vehicle ORDER BY RegistrationNumber ASC")
    vehicles_ = cur.fetchall()
    cur.execute("SELECT ServiceID, ServiceName FROM Service ORDER BY ServiceName ASC")
    services_ = cur.fetchall()
    cur.execute("SELECT MechanicID, MechanicName FROM Mechanic ORDER BY MechanicName ASC")
    mechanics_ = cur.fetchall()

    if request.method == "POST":
        vehicle_id = request.form["vehicle_id"]
        service_id = request.form["service_id"]
        mechanic_id = request.form["mechanic_id"]
        service_date = request.form["service_date"]
        status = request.form["status"]

        cur.execute("""
            UPDATE Service_Record
            SET VehicleID=%s, ServiceID=%s, MechanicID=%s, ServiceDate=%s, Status=%s
            WHERE RecordID=%s
        """, (vehicle_id, service_id, mechanic_id, service_date, status, record_id))
        conn.commit()

        # Reset the AUTO_INCREMENT after editing a record
        cur.execute("SELECT MAX(RecordID) FROM Service_Record")
        max_id = cur.fetchone()[0]
        cur.execute(f"ALTER TABLE Service_Record AUTO_INCREMENT = {max_id + 1}")
        
        conn.commit()
        cur.close()
        conn.close()
        return redirect("/records")

    v_id, s_id, m_id, sdate, status0 = row

    v_opts = "".join([f'<option value="{v[0]}"{ "selected" if v[0]==v_id else ""}>{escape(v[1])}</option>' for v in vehicles_])
    s_opts = "".join([f'<option value="{s[0]}"{ "selected" if s[0]==s_id else ""}>{escape(s[1])}</option>' for s in services_])
    m_opts = "".join([f'<option value="{m[0]}"{ "selected" if m[0]==m_id else ""}>{escape(m[1])}</option>' for m in mechanics_])

    cur.close()
    conn.close()

    body = f"""
    <div class="card">
      <form method="post">
        <div class="field"><label>Vehicle</label><select name="vehicle_id" required>{v_opts}</select></div>
        <div class="field"><label>Service</label><select name="service_id" required>{s_opts}</select></div>
        <div class="field"><label>Mechanic</label><select name="mechanic_id" required>{m_opts}</select></div>
        <div class="field"><label>Service Date</label><input type="date" name="service_date" value="{escape(str(sdate))}" required></div>
        <div class="field">
          <label>Status</label>
          <select name="status">
            <option {"selected" if status0=="Pending" else ""}>Pending</option>
            <option {"selected" if status0=="In Progress" else ""}>In Progress</option>
            <option {"selected" if status0=="Completed" else ""}>Completed</option>
          </select>
        </div>
        <div class="actions">
          <button class="btn primary" type="submit">Update</button>
          <a class="btn" href="/records">Cancel</a>
        </div>
      </form>
    </div>
    """
    return render_page("Edit Service Record", "/records", body)
