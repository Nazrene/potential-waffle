from flask import Flask, jsonify, request
from models import db, Episode, Guest, Appearance

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///late_show.db'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/', methods=['GET'])
def home():
    return jsonify(message="Welcome to the Late Show API! Use /episodes, /guests, and /appearances.")

@app.route('/episodes', methods=['GET'])
def get_episodes():
    episodes = Episode.query.all()
    return jsonify([{"id": episode.id, "date": episode.date, "number": episode.number} for episode in episodes])

@app.route('/episodes/<int:id>', methods=['GET'])
def get_episode(id):
    episode = Episode.query.get(id)
    if not episode:
        return jsonify({"error": "Episode not found"}), 404

    appearances = [
        {
            "episode_id": appearance.episode_id,
            "guest_id": appearance.guest_id,
            "rating": appearance.rating,
            "id": appearance.id
        }
        for appearance in episode.appearances
    ]

    return jsonify({
        "id": episode.id,
        "date": episode.date,
        "number": episode.number,
        "appearances": appearances
    })

@app.route('/episodes/<int:id>', methods=['DELETE'])
def delete_episode(id):
    episode = Episode.query.get(id)
    if not episode:
        return jsonify({"error": "Episode not found"}), 404

    db.session.delete(episode)
    db.session.commit()
    return jsonify({"message": f"Episode {id} has been deleted"}), 200

@app.route('/guests', methods=['GET'])
def get_guests():
    guests = Guest.query.all()
    return jsonify([{"id": guest.id, "name": guest.name, "occupation": guest.occupation} for guest in guests])

@app.route('/appearances', methods=['POST'])
def create_appearance():
    data = request.get_json()
    if not data or 'rating' not in data or 'episode_id' not in data or 'guest_id' not in data:
        return jsonify({"error": "Missing fields in request"}), 400

    try:
        new_appearance = Appearance(
            rating=data['rating'],
            episode_id=data['episode_id'],
            guest_id=data['guest_id']
        )
        db.session.add(new_appearance)
        db.session.commit()

    except ValueError as error_message:
        db.session.rollback()
        return jsonify({"error": str(error_message)}), 400

    return jsonify({
        "id": new_appearance.id,
        "rating": new_appearance.rating,
        "episode_id": new_appearance.episode_id,
        "guest_id": new_appearance.guest_id
    }), 201

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  
    app.run(debug=True)
