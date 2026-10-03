from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)

# Secret key is required for Flask sessions
app.secret_key = "smart-campus-secret-key"


# =========================
# Home Page
# =========================

@app.route("/")
def home():
    return render_template("index.html")


# =========================
# Report Problem Page
# =========================

@app.route("/report")
def report():
    return render_template("report.html")


# =========================
# My Complaints Page
# =========================

@app.route("/complaints")
def complaints():
    connection = sqlite3.connect("smart_campus.db")
    cursor = connection.cursor()

    # Show newest complaints first
    cursor.execute("SELECT * FROM complaints ORDER BY id DESC")
    complaints = cursor.fetchall()

    connection.close()

    return render_template("complaints.html", complaints=complaints)


# =========================
# Submit Complaint
# =========================

@app.route("/submit-complaint", methods=["POST"])
def submit_complaint():

    # Get all form fields
    student_name = request.form.get("name")
    department = request.form.get("department")
    problem_type = request.form.get("problem")
    location = request.form.get("location")
    complaint_text = request.form.get("description")
    priority = request.form.get("priority")

    connection = sqlite3.connect("smart_campus.db")
    cursor = connection.cursor()

    # Generate the next Complaint ID
    cursor.execute("""
        SELECT complaint_id
        FROM complaints
        ORDER BY id DESC
        LIMIT 1
    """)

    last_complaint = cursor.fetchone()

    if last_complaint:
        last_number = int(last_complaint[0].replace("CMP", ""))
        complaint_id = f"CMP{last_number + 1}"
    else:
        complaint_id = "CMP1026"

    # Save complaint to database
    cursor.execute("""
        INSERT INTO complaints
        (complaint_id, student_name, department, problem_type,
         location, complaint_text, priority, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        complaint_id,
        student_name,
        department,
        problem_type,
        location,
        complaint_text,
        priority,
        "Pending"
    ))

    connection.commit()
    connection.close()

    # Show success page
    return render_template(
        "success.html",
        complaint_id=complaint_id
    )


# =========================
# Admin Login
# =========================

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "admin123":

            session["admin_logged_in"] = True

            return redirect(url_for("admin_dashboard"))

        else:

            return "Invalid username or password"

    return render_template("admin-login.html")


# =========================
# Admin Dashboard
# =========================

@app.route("/admin-dashboard")
def admin_dashboard():

    # Protect dashboard
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    connection = sqlite3.connect("smart_campus.db")
    cursor = connection.cursor()

    # Get all complaints
    cursor.execute("""
        SELECT * FROM complaints
        ORDER BY id DESC
    """)
    complaints = cursor.fetchall()

    # Total complaints
    cursor.execute("""
        SELECT COUNT(*) FROM complaints
    """)
    total_complaints = cursor.fetchone()[0]

    # Pending complaints
    cursor.execute("""
        SELECT COUNT(*) FROM complaints
        WHERE status = 'Pending'
    """)
    pending = cursor.fetchone()[0]

    # In Progress complaints
    cursor.execute("""
        SELECT COUNT(*) FROM complaints
        WHERE status = 'In Progress'
    """)
    in_progress = cursor.fetchone()[0]

    # Resolved complaints
    cursor.execute("""
        SELECT COUNT(*) FROM complaints
        WHERE status = 'Resolved'
    """)
    resolved = cursor.fetchone()[0]

    connection.close()

    return render_template(
        "admin-dashboard.html",
        complaints=complaints,
        total_complaints=total_complaints,
        pending=pending,
        in_progress=in_progress,
        resolved=resolved
    )


# =========================
# Update Complaint Status
# =========================

@app.route("/update-status", methods=["POST"])
def update_status():

    # Only logged-in admin can update status
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    complaint_id = request.form.get("complaint_id")
    status = request.form.get("status")

    # Allowed statuses
    allowed_statuses = [
        "Pending",
        "In Progress",
        "Resolved"
    ]

    if status not in allowed_statuses:
        return "Invalid status"

    connection = sqlite3.connect("smart_campus.db")
    cursor = connection.cursor()

    # Update status in database
    cursor.execute("""
        UPDATE complaints
        SET status = ?
        WHERE complaint_id = ?
    """, (
        status,
        complaint_id
    ))

    connection.commit()
    connection.close()

    # Return to dashboard
    return redirect(url_for("admin_dashboard"))


# =========================
# Admin Logout
# =========================

@app.route("/admin-logout")
def admin_logout():

    # Remove admin login session
    session.pop("admin_logged_in", None)

    # Go back to admin login
    return redirect(url_for("admin_login"))


# =========================
# Run Flask Application
# =========================

if __name__ == "__main__":
    app.run(debug=True)
