from flask import Blueprint, request, redirect
from markupsafe import escape

from db import get_conn
from ui import render_page, table

bp = Blueprint("bills", __name__)

# -------------------- BILLS LIST --------------------
@bp.route("/bills")
def bills():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT b.BillID,
               b.RecordID,
               c.CustomerName,
               COALESCE(v.VehicleModel, '') AS VehicleModel,
               COALESCE(v.RegistrationNumber, '') AS RegistrationNumber,
               s.ServiceName,
               b.TotalAmount,
               b.PaymentStatus,
               b.BillDate
        FROM Bill b
        JOIN Service_Record sr ON b.RecordID = sr.RecordID
        JOIN Vehicle v ON sr.VehicleID = v.VehicleID
        JOIN Customer c ON v.CustomerID = c.CustomerID
        JOIN Service s ON sr.ServiceID = s.ServiceID
        ORDER BY b.BillID ASC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    actions = """
    <div class="card">
      <div class="actions">
        <a class="btn primary" href="/add-bill">+ Create Bill</a>
      </div>
      <div class="footer-note">Receipt opens a printable invoice. Toggle Paid switches between Paid/Unpaid.</div>
    </div>
    """

    def row_html(r):
        bid, rid, cname, vmodel, reg, sname, total, status, bdate = r
        badge = f"<span class='badge'>{escape(status)}</span>"
        vehicle_display = f"{vmodel} ({reg})".strip() if (vmodel or reg) else ""

        return (
            f"<tr>"
            f"<td>{bid}</td>"
            f"<td>{rid}</td>"
            f"<td>{escape(cname)}</td>"
            f"<td>{escape(vehicle_display)}</td>"
            f"<td>{escape(sname)}</td>"
            f"<td>{escape(str(total))}</td>"
            f"<td>{badge}</td>"
            f"<td>{escape(str(bdate))}</td>"
            f"<td style='display:flex; gap:8px; align-items:center;'>"
            f"<a class='btn' href='/receipt/{bid}' target='_blank'>Receipt</a>"
            f"<a class='btn' href='/toggle-bill/{bid}'>Toggle Paid</a>"
            f"</td>"
            f"</tr>"
        )

    t = table(
        ["Bill ID", "Record ID", "Customer", "Vehicle", "Service", "Total", "Status", "Bill Date", "Actions"],
        rows,
        row_html
    )
    return render_page("Bills", "/bills", actions + t, "Generate bills from service records")

# -------------------- ADD BILL --------------------
@bp.route("/add-bill", methods=["GET", "POST"])
def add_bill():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT sr.RecordID, s.ServiceName, s.Cost
        FROM Service_Record sr
        JOIN Service s ON sr.ServiceID = s.ServiceID
        ORDER BY sr.RecordID ASC
    """)
    records_ = cur.fetchall()

    if request.method == "POST":
        record_id = request.form["record_id"]

        cur.execute("""
            SELECT s.Cost
            FROM Service_Record sr
            JOIN Service s ON sr.ServiceID = s.ServiceID
            WHERE sr.RecordID = %s
        """, (record_id,))
        cost = cur.fetchone()[0]

        cur.execute(
            """INSERT INTO Bill (RecordID, TotalAmount, PaymentStatus, BillDate)
               VALUES (%s, %s, 'Unpaid', CURDATE())""",
            (record_id, cost)
        )
        conn.commit()

        # Reset the AUTO_INCREMENT after inserting a new record
        cur.execute("SELECT MAX(BillID) FROM Bill")
        max_id = cur.fetchone()[0]
        if max_id is None:  # If the table is empty
            cur.execute("ALTER TABLE Bill AUTO_INCREMENT = 1")
        else:
            cur.execute(f"ALTER TABLE Bill AUTO_INCREMENT = {max_id + 1}")

        conn.commit()
        cur.close()
        conn.close()
        return redirect("/bills")

    options = "".join([f'<option value="{r[0]}">Record {r[0]} — {escape(r[1])} — {escape(str(r[2]))}</option>' for r in records_])

    cur.close()
    conn.close()

    body = f"""
    <div class="card">
      <form method="post">
        <div class="field"><label>Service Record</label><select name="record_id" required>{options}</select></div>
        <div class="actions">
          <button class="btn primary" type="submit">Create Bill</button>
          <a class="btn" href="/bills">Cancel</a>
        </div>
      </form>
    </div>
    """
    return render_page("Create Bill", "/bills", body)

# -------------------- TOGGLE BILL --------------------
@bp.route("/toggle-bill/<int:bill_id>")
def toggle_bill(bill_id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT PaymentStatus FROM Bill WHERE BillID = %s", (bill_id,))
    status = cur.fetchone()[0]
    new_status = "Paid" if status != "Paid" else "Unpaid"

    cur.execute("UPDATE Bill SET PaymentStatus = %s WHERE BillID = %s", (new_status, bill_id))
    conn.commit()

    cur.close()
    conn.close()
    return redirect("/bills")

# -------------------- RECEIPT --------------------
@bp.route("/receipt/<int:bill_id>")
def receipt(bill_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT b.BillID,
               b.BillDate,
               b.PaymentStatus,
               b.TotalAmount,
               c.CustomerName,
               c.PhoneNumber,
               COALESCE(c.Address,''),
               COALESCE(v.VehicleModel,''),
               COALESCE(v.RegistrationNumber,''),
               COALESCE(v.ManufacturingYear,''),
               s.ServiceName,
               s.Cost,
               m.MechanicName,
               sr.ServiceDate,
               sr.Status
        FROM Bill b
        JOIN Service_Record sr ON b.RecordID = sr.RecordID
        JOIN Vehicle v ON sr.VehicleID = v.VehicleID
        JOIN Customer c ON v.CustomerID = c.CustomerID
        JOIN Service s ON sr.ServiceID = s.ServiceID
        JOIN Mechanic m ON sr.MechanicID = m.MechanicID
        WHERE b.BillID = %s
    """, (bill_id,))
    r = cur.fetchone()
    cur.close()
    conn.close()

    if not r:
        return redirect("/bills")

    (bid, bdate, paystatus, total, cname, phone, addr,
     vmodel, reg, year, sname, cost, mech, sdate, srstatus) = r

    receipt_css = """
    <style>
    body {
        background: #f4f4f4;
        color: #000;
        font-family: "Courier New", Courier, monospace;
        font-weight: 500;
    }

    .wrap {
        max-width: 420px;
        margin: 24px auto;
        padding: 18px;
        background: #fff;
        border: 2px solid #000;
    }

    .center {
        text-align: center;
        font-weight: 700;
    }

    .small {
        font-size: 12px;
        font-weight: 600;
    }

    .hr {
        border-top: 2px dashed #000;
        margin: 14px 0;
    }

    .row {
        display: flex;
        justify-content: space-between;
        font-size: 14px;
        font-weight: 600;
        margin: 4px 0;
    }

    .row b {
        font-weight: 800;
    }

    .btns {
        text-align: center;
        margin-top: 14px;
    }

    button {
        padding: 8px 14px;
        font-weight: 700;
        cursor: pointer;
        border: 2px solid #000;
        background: #fff;
    }

    @media print {
        body {
        background: #fff;
        }
        .btns {
        display: none;
        }
        .wrap {
        border: none;
        margin: 0;
        padding: 10px;
        }
    }
    </style>
    """

    return f"""
    <!doctype html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>Receipt #{bid}</title>
      {receipt_css}
    </head>
    <body>
      <div class="wrap">
        <div class="center">
          <b>WORKSHOP MANAGER</b><br>
          <span class="small">Receipt</span>
        </div>

        <div class="hr"></div>

        <div class="row"><span>Receipt #</span><b>{bid}</b></div>
        <div class="row"><span>Date</span><b>{escape(str(bdate))}</b></div>
        <div class="row"><span>Status</span><b>{escape(paystatus)}</b></div>

        <div class="hr"></div>

        <div class="small"><b>Customer</b></div>
        <div>{escape(cname)}</div>
        <div>{escape(phone)}</div>

        <div class="hr"></div>

        <div class="small"><b>Vehicle</b></div>
        <div>{escape(vmodel)} ({escape(reg)})</div>

        <div class="hr"></div>

        <div class="small"><b>Service</b></div>
        <div>{escape(sname)}</div>
        <div>Mechanic: {escape(mech)}</div>

        <div class="hr"></div>

        <div class="row"><span>Total</span><b>{escape(str(total))}</b></div>

        <div class="hr"></div>

        <div class="center small">Thank you for your business</div>

        <div class="btns">
          <button onclick="window.print()">Print</button>
        </div>
      </div>
    </body>
    </html>
    """
