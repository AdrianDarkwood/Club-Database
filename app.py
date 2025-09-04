from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import inspect, or_
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --------------------
# Models
# --------------------
class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    branch = db.Column(db.String(50))
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Members 1-6
    for i in range(1, 7):
        vars()[f'member{i}_name'] = db.Column(db.String(100))
        vars()[f'member{i}_usn'] = db.Column(db.String(50))
        vars()[f'member{i}_phone'] = db.Column(db.String(20))

# --------------------
# Create tables if not exists
# --------------------
with app.app_context():
    inspector = inspect(db.engine)
    if not inspector.has_table("registration"):
        db.create_all()

# --------------------
# Routes
# --------------------
@app.route('/', methods=['GET'])
def admin():
    search = request.args.get('search', '')
    branch_filter = request.args.get('branch', '')

    query = Registration.query
    if search:
        conditions = []
        for i in range(1,7):
            conditions.append(getattr(Registration, f'member{i}_name').ilike(f'%{search}%'))
            conditions.append(getattr(Registration, f'member{i}_usn').ilike(f'%{search}%'))
        query = query.filter(or_(*conditions))

    if branch_filter:
        query = query.filter_by(branch=branch_filter)

    entries = query.order_by(Registration.submitted_at.desc()).all()

    # get unique branches
    branches = [b[0] for b in db.session.query(Registration.branch).distinct().all() if b[0]]

    return render_template('admin.html', entries=entries, branches=branches)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_entry(id):
    entry = Registration.query.get_or_404(id)
    db.session.delete(entry)
    db.session.commit()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)
