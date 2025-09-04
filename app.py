from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import inspect

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'YOUR_DATABASE_URL'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --------------------
# Models
# --------------------
class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member1_name = db.Column(db.String(100), nullable=False)
    member1_usn = db.Column(db.String(50), nullable=False)
    member1_phone = db.Column(db.String(20), nullable=False)
    branch = db.Column(db.String(50))
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

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
@app.route('/')
def admin():
    entries = Registration.query.order_by(Registration.submitted_at.desc()).all()
    return render_template('admin.html', entries=entries)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_entry(id):
    entry = Registration.query.get_or_404(id)
    db.session.delete(entry)
    db.session.commit()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)
