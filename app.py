from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///late_show.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Episode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String, nullable=False)
    number = db.Column(db.Integer, nullable=False)
    appearances = db.relationship('Appearance', backref='episode', cascade="all, delete-orphan")

class Guest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    occupation = db.Column(db.String, nullable=False)
    appearances = db.relationship('Appearance', backref='guest', cascade="all, delete-orphan")

class Appearance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    episode_id = db.Column(db.Integer, db.ForeignKey('episode.id'), nullable=False)
    guest_id = db.Column(db.Integer, db.ForeignKey('guest.id'), nullable=False)

# Define Routes
@app.route('/', methods=['GET'])
def home():
    return "Welcome to the Late Show API! Use /episodes, /guests, and /appearances."

@app.route('/episodes', methods=['GET'])
def get_episodes():
    episodes = Episode.query.all()
    return jsonify([{"id": ep.id, "date": ep.date, "number": ep.number} for ep in episodes])

@app.route('/episodes/<int:id>', methods=['GET'])
def get_episode(id):
    episode = Episode.query.get(id)
    if not episode:
        return make_response({"error": "Episode not found"}, 404)

    appearances = []
    for appearance in episode.appearances:
        appearances.append({
            "episode_id": appearance.episode_id,
            "guest_id": appearance.guest_id,
            "rating": appearance.rating,
            "id": appearance.id
        })

    return jsonify({
        "id": episode.id,
        "date": episode.date,
        "number": episode.number,
        "appearances": appearances
    })

@app.route('/guests', methods=['GET'])
def get_guests():
    guests = Guest.query.all()
    return jsonify([{"id": g.id, "name": g.name, "occupation": g.occupation} for g in guests])

@app.route('/appearances', methods=['POST'])
def create_appearance():
    data = request.get_json()
    if not data or 'rating' not in data or 'episode_id' not in data or 'guest_id' not in data:
        return make_response({"error": "Missing fields in request"}, 400)

    rating = data['rating']
    if rating < 1 or rating > 5:
        return make_response({"error": "Rating must be between 1 and 5."}, 400)

    new_appearance = Appearance(
        rating=rating,
        episode_id=data['episode_id'],
        guest_id=data['guest_id']
    )

    db.session.add(new_appearance)
    db.session.commit()

    return jsonify({
        "id": new_appearance.id,
        "rating": new_appearance.rating,
        "episode_id": new_appearance.episode_id,
        "guest_id": new_appearance.guest_id
    }), 201

if __name__ == '__main__':
    app.run(debug=True)