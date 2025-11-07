from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from config import Config
from models import init_db, SessionLocal, User, FoodDonation, FoodRequest, Vehicle, Match

# Agents
from agents.data_ingestion import DataIngestionAgent
from agents.matching import MatchingAgent
from agents.logistics import LogisticsAgent
from agents.monitoring import MonitoringAgent

import json

app = Flask(__name__)
app.config["SECRET_KEY"] = Config.SECRET_KEY

# AI Agents
ingestion_agent = DataIngestionAgent()
matching_agent = MatchingAgent()
logistics_agent = LogisticsAgent()
monitoring_agent = MonitoringAgent()

# Initialize DB & seed vehicles
init_db()
with SessionLocal() as db:
    if db.query(Vehicle).count() == 0:
        db.add_all([
            Vehicle(name="Van-1", capacity_meals=80, base_lat=15.8528, base_lon=74.4987),
            Vehicle(name="Bike-1", capacity_meals=30, base_lat=15.8528, base_lon=74.4987),
        ])
        db.commit()


# ------------- SESSION USER ----------
def current_user(db):
    if "user_email" not in session:
        return None
    return db.get(User, session["user_email"])


# ------------- ROUTES --------------

@app.route("/")
def index():
    return render_template("index.html")


# ---------- REGISTER ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        name = request.form["name"].strip()
        phone = request.form["phone"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        role = request.form["role"]
        prefers_veg = request.form.get("prefers_veg", "true") == "true"

        # FIXED
        district = "Belagavi"
        state = "Karnataka"

        # User input
        taluk = request.form["taluk"].strip()
        pincode = request.form["pincode"].strip()
        address_line = request.form["address"].strip()

        # ✅ Allowed taluks in Belagavi district
        belagavi_taluks = {
            "Belagavi", "Gokak", "Khanapur", "Ramdurg", "Saundatti",
            "Bailhongal", "Athani", "Chikkodi", "Raibag", "Hukkeri"
        }

        if taluk not in belagavi_taluks:
            flash("Only Belagavi district taluks are allowed.")
            return redirect(url_for("register"))

        # ✅ Taluk → Coordinates
        taluk_coordinates = {
            "Belagavi": (15.8497, 74.4977),
            "Gokak": (16.1691, 74.5146),
            "Khanapur": (15.6390, 74.5089),
            "Ramdurg": (15.9481, 75.2980),
            "Saundatti": (15.7525, 75.1177),
            "Bailhongal": (15.8222, 74.8580),
            "Athani": (16.7260, 75.0648),
            "Chikkodi": (16.4296, 74.6009),
            "Raibag": (16.4918, 74.7845),
            "Hukkeri": (16.2300, 74.6000)
        }

        lat, lon = taluk_coordinates[taluk]

        # ✅ AI agent validation
        res = ingestion_agent.validate_user_address({
            "district": district,
            "taluk": taluk,
            "pincode": pincode
        })

        if not res.ok:
            flash(res.reason)
            return redirect(url_for("register"))

        with SessionLocal() as db:

            # ✅ Duplicate email check
            if db.get(User, email):
                flash("Email already registered.")
                return redirect(url_for("login"))

            # Build full address
            full_addr = f"{address_line}, {taluk}, {district}, {state}, {pincode}"

            user = User(
                email=email,
                name=name,
                phone=phone,
                address=full_addr,
                pincode=pincode,
                role=role,
                password_hash=generate_password_hash(password),
            )

            db.add(user)
            db.commit()

        flash("Registration successful. Please login.")
        return redirect(url_for("login"))

    return render_template("register.html")


# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].lower()
        password = request.form["password"]

        with SessionLocal() as db:
            user = db.get(User, email)
            if not user or not check_password_hash(user.password_hash, password):
                flash("Invalid email or password.")
                return redirect(url_for("login"))

            # ✅ Store correct session key
            session["user_email"] = user.email

        return redirect(url_for("portal"))

    return render_template("login.html")

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        with SessionLocal() as db:
            user = db.get(User, email)

            # Check if admin
            if not user or user.role != "admin":
                flash("Invalid admin account.")
                return redirect(url_for("admin_login"))

            if not check_password_hash(user.password_hash, password):
                flash("Incorrect password.")
                return redirect(url_for("admin_login"))

            # Admin session
            session["admin"] = user.email
            flash("Welcome Admin!")
            return redirect(url_for("dashboard"))

    return render_template("admin-login.html")

# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.pop("user_email", None)
    flash("Logged out.")
    return redirect(url_for("index"))

@app.route("/admin-logout")
def admin_logout():
    session.pop("admin", None)
    flash("Admin logged out.")
    return redirect(url_for("index"))

# ---------- PORTAL ----------
@app.route("/portal")
def portal():
    with SessionLocal() as db:
        user = current_user(db)
        if not user:
            flash("Please login.")
            return redirect(url_for("login"))

        # Build activity list
        activity = []
        for d in user.donations:
            activity.append({"type": "Donation", "details": d.title, "status": d.status})
        for r in user.requests:
            activity.append({"type": "Request", "details": f"{r.need_meals} meals", "status": r.status})

        return render_template("portal.html", user=user, activity=activity)



# ✅ ✅ ✅ ADD DONATE-PAGE (GET)
@app.route("/donate-page")
def donate_page():
    with SessionLocal() as db:
        u = current_user(db)
        if not u or u.role != "donor":
            flash("Only donors can donate.")
            return redirect(url_for("portal"))
        return render_template("donate-page.html", user=u)



# ✅ ✅ ✅ ADD REQUEST-PAGE (GET)
@app.route("/request-page")
def request_page():
    with SessionLocal() as db:
        u = current_user(db)
        if not u or u.role != "recipient":
            flash("Only recipients can request food.")
            return redirect(url_for("portal"))
        return render_template("request-page.html", user=u)



# ---------- DONATE (POST ONLY) ----------
@app.post("/donate")
def donate():
    with SessionLocal() as db:
        user = current_user(db)
        if not user or user.role != "donor":
            flash("Only donors can donate.")
            return redirect(url_for("portal"))

        donation = FoodDonation(
            donor_email=user.email,
            title=request.form["title"],
            description=request.form.get("description", ""),
            is_veg=request.form.get("is_veg", "true") == "true",
            quantity_meals=int(request.form["quantity"]),
            ready_by=datetime.fromisoformat(request.form["ready_by"]),
            expire_by=datetime.fromisoformat(request.form["expire_by"]),
            address=user.address,
            pincode=user.pincode,
            lat=15.8497,
            lon=74.4977,
        )

        db.add(donation)
        db.commit()

    flash("Donation posted.")
    return redirect(url_for("portal"))


# ---------- REQUEST FOOD (POST ONLY) ----------
@app.post("/request-food")
def request_food():
    with SessionLocal() as db:
        user = current_user(db)
        if not user or user.role != "recipient":
            flash("Only recipients can request.")
            return redirect(url_for("portal"))

        req = FoodRequest(
            recipient_email=user.email,
            need_meals=int(request.form["need_meals"]),
            prefers_veg=request.form.get("prefers_veg", "true") == "true",
            earliest=datetime.fromisoformat(request.form["earliest"]),
            latest=datetime.fromisoformat(request.form["latest"]),
            address=user.address,
            pincode=user.pincode,
            lat=15.8570,
            lon=74.5060,
        )

        db.add(req)
        db.commit()

    flash("Request submitted.")
    return redirect(url_for("portal"))


# ---------- ADMIN DASHBOARD ----------
@app.route("/dashboard")
def dashboard():
    if "admin" not in session:
        flash("Admin access only.")
        return redirect(url_for("admin-login"))

    with SessionLocal() as db:
        donations = db.query(FoodDonation).filter(FoodDonation.status=="open").all()
        requests = db.query(FoodRequest).filter(FoodRequest.status=="open").all()
        matches = db.query(Match).all()
        vehicles = db.query(Vehicle).filter(Vehicle.is_available==True).all()

        return render_template("dashboard.html",
            donations=donations, requests=requests, matches=matches, vehicles=vehicles)


# ---------- MATCH ----------
@app.post("/match/<int:donation_id>")
def create_match(donation_id):
    req_id = int(request.form["request_id"])
    with SessionLocal() as db:
        d = db.get(FoodDonation, donation_id)
        r = db.get(FoodRequest, req_id)

        score_info = matching_agent.score(d, r)

        match = Match(
            donation_id=d.id,
            request_id=r.id,
            score=score_info.score,
            status="planned"
        )

        d.status = "matched"
        r.status = "matched"

        db.add(match)
        db.commit()

    flash("Match created.")
    return redirect(url_for("dashboard"))


# ---------- ASSIGN VEHICLE ----------
@app.post("/assign/<int:match_id>")
def assign_vehicle(match_id):
    vehicle_id = int(request.form["vehicle_id"])
    with SessionLocal() as db:
        m = db.get(Match, match_id)
        v = db.get(Vehicle, vehicle_id)

        d = m.donation
        r = m.request

        route = logistics_agent.nearest_neighbor(
            v.base_lat, v.base_lon, [
                (d.lat, d.lon),
                (r.lat, r.lon)
            ]
        )

        m.vehicle_id = v.id
        m.route_json = json.dumps({"order": route.order, "km": route.total_km})
        m.status = "assigned"

        db.commit()

    flash("Vehicle assigned.")
    return redirect(url_for("dashboard"))


# ---------- UPDATE MATCH STATUS ----------
@app.post("/status/<int:match_id>")
def update_status(match_id):
    new_status = request.form["status"]
    with SessionLocal() as db:
        m = db.get(Match, match_id)

        m.status = new_status

        if new_status == "delivered":
            m.donation.status = "delivered"
            m.request.status = "fulfilled"

        db.commit()

    flash("Status updated.")
    return redirect(url_for("dashboard"))

@app.post("/delete/<int:match_id>")
def delete_match(match_id):
    with SessionLocal() as db:
        m = db.get(Match, match_id)

        if m.status != "delivered":
            flash("You can delete only delivered records.")
            return redirect(url_for("dashboard"))

        db.delete(m)
        db.commit()

    flash("Record deleted successfully.")
    return redirect(url_for("dashboard"))

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)
