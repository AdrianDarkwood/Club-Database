from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --------------------
# Models (must match Service A exactly)
# --------------------
class Registration(db.Model):
    __tablename__ = "registrations"

    id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(200), nullable=False)

    # Member 1 (required)
    member1_name = db.Column(db.String(100), nullable=False)
    member1_email = db.Column(db.String(100), nullable=False)
    member1_usn = db.Column(db.String(100), nullable=False)
    member1_phone = db.Column(db.String(20))
    member1_branch = db.Column(db.String(50), nullable=False)

    # Member 2–6 (optional)
    member2_name = db.Column(db.String(100))
    member2_email = db.Column(db.String(100))
    member2_usn = db.Column(db.String(100))
    member2_phone = db.Column(db.String(20))
    member2_branch = db.Column(db.String(50))

    member3_name = db.Column(db.String(100))
    member3_email = db.Column(db.String(100))
    member3_usn = db.Column(db.String(100))
    member3_phone = db.Column(db.String(20))
    member3_branch = db.Column(db.String(50))

    member4_name = db.Column(db.String(100))
    member4_email = db.Column(db.String(100))
    member4_usn = db.Column(db.String(100))
    member4_phone = db.Column(db.String(20))
    member4_branch = db.Column(db.String(50))

    member5_name = db.Column(db.String(100))
    member5_email = db.Column(db.String(100))
    member5_usn = db.Column(db.String(100))
    member5_phone = db.Column(db.String(20))
    member5_branch = db.Column(db.String(50))

    member6_name = db.Column(db.String(100))
    member6_email = db.Column(db.String(100))
    member6_usn = db.Column(db.String(100))
    member6_phone = db.Column(db.String(20))
    member6_branch = db.Column(db.String(50))

    submitted_at = db.Column(db.DateTime)

# --------------------
# ⚠️ Important: Don't run create_all() in Service B
# --------------------
# Service A owns schema & migrations
# Service B should only read/query existing data

# --------------------
# Routes
# --------------------
@app.route('/', methods=['GET'])
def admin():
    search = request.args.get('search', '')
    branch_filter = request.args.get('branch', '')

    query = Registration.query

    # Search across all member names & USNs
    if search:
        conditions = []
        for i in range(1, 7):
            conditions.append(getattr(Registration, f'member{i}_name').ilike(f'%{search}%'))
            conditions.append(getattr(Registration, f'member{i}_usn').ilike(f'%{search}%'))
        query = query.filter(or_(*conditions))

    # Branch filter across all members
    if branch_filter:
        branch_conditions = [
            getattr(Registration, f'member{i}_branch') == branch_filter
            for i in range(1, 7)
        ]
        query = query.filter(or_(*branch_conditions))

    entries = query.order_by(Registration.submitted_at.desc()).all()

    # Collect unique branches across all members
    branches = set()
    for i in range(1, 7):
        results = db.session.query(getattr(Registration, f'member{i}_branch')).distinct().all()
        branches.update([r[0] for r in results if r[0]])

    return render_template('admin.html', entries=entries, branches=sorted(branches))

@app.route('/delete/<int:id>', methods=['POST'])
def delete_entry(id):
    entry = Registration.query.get_or_404(id)
    db.session.delete(entry)
    db.session.commit()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)
