from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/retreats_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Retreat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)
    price = db.Column(db.Numeric, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    details = db.Column(db.Text, nullable=True)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    user_name = db.Column(db.String, nullable=False)
    user_email = db.Column(db.String, nullable=False)
    user_phone = db.Column(db.String, nullable=False)
    retreat_id = db.Column(db.Integer, db.ForeignKey('retreat.id'), nullable=False)
    retreat_title = db.Column(db.String, nullable=False)
    retreat_location = db.Column(db.String, nullable=False)
    retreat_price = db.Column(db.Numeric, nullable=False)
    retreat_duration = db.Column(db.Integer, nullable=False)
    payment_details = db.Column(db.Text, nullable=False)
    booking_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

@app.route('/retreats', methods=['GET'])
def get_retreats():
    filter_criteria = request.args
    query = Retreat.query

    if 'search' in filter_criteria:
        search_term = filter_criteria['search']
        query = query.filter(Retreat.title.ilike(f'%{search_term}%') | Retreat.details.ilike(f'%{search_term}%'))

    if 'location' in filter_criteria:
        location = filter_criteria['location']
        query = query.filter_by(location=location)

    page = int(filter_criteria.get('page', 1))
    limit = int(filter_criteria.get('limit', 10))

    retreats = query.paginate(page, limit, False).items
    result = [retreat.__dict__ for retreat in retreats]

    return jsonify(result)

@app.route('/book', methods=['POST'])
def book_retreat():
    data = request.json
    booking = Booking(**data)

    existing_booking = Booking.query.filter_by(user_id=data['user_id'], retreat_id=data['retreat_id']).first()
    if existing_booking:
        return jsonify({'error': 'Retreat already booked by this user'}), 400

    db.session.add(booking)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Could not book retreat'}), 500

    return jsonify({'message': 'Booking successful'}), 201

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
