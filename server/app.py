"""
EventWise Flask Application
Provides REST API endpoints for managing events, sessions, and speakers
"""
from flask import Flask, jsonify, make_response
from flask_migrate import Migrate
from models import db, Event, Session, Speaker, Bio

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eventwise.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# Initialize extensions
migrate = Migrate(app, db)
db.init_app(app)


# ==================== Event Endpoints ====================

@app.route('/events', methods=['GET'])
def get_events():
    """
    GET /events
    Returns a list of all events with id, name, and location
    """
    events = Event.query.all()
    events_list = [
        {
            'id': event.id,
            'name': event.name,
            'location': event.location
        }
        for event in events
    ]
    return make_response(jsonify(events_list), 200)


@app.route('/events/<int:id>/sessions', methods=['GET'])
def get_event_sessions(id):
    """
    GET /events/<int:id>/sessions
    Returns all sessions for a specific event
    Returns 404 if event not found
    """
    event = Event.query.get(id)
    
    if not event:
        return make_response(jsonify({'error': 'Event not found'}), 404)
    
    sessions_list = [
        {
            'id': session.id,
            'title': session.title,
            'start_time': session.start_time.isoformat()
        }
        for session in event.sessions
    ]
    return make_response(jsonify(sessions_list), 200)


# ==================== Speaker Endpoints ====================

@app.route('/speakers', methods=['GET'])
def get_speakers():
    """
    GET /speakers
    Returns a list of all speakers with id and name
    """
    speakers = Speaker.query.all()
    speakers_list = [
        {
            'id': speaker.id,
            'name': speaker.name
        }
        for speaker in speakers
    ]
    return make_response(jsonify(speakers_list), 200)


@app.route('/speakers/<int:id>', methods=['GET'])
def get_speaker(id):
    """
    GET /speakers/<int:id>
    Returns a speaker with their bio
    Returns 404 if speaker not found
    """
    speaker = Speaker.query.get(id)
    
    if not speaker:
        return make_response(jsonify({'error': 'Speaker not found'}), 404)
    
    speaker_data = {
        'id': speaker.id,
        'name': speaker.name,
        'bio_text': speaker.bio.bio_text if speaker.bio else 'No bio available'
    }
    return make_response(jsonify(speaker_data), 200)


# ==================== Session Endpoints ====================

@app.route('/sessions/<int:id>/speakers', methods=['GET'])
def get_session_speakers(id):
    """
    GET /sessions/<int:id>/speakers
    Returns a list of speakers for a specific session
    Returns 404 if session not found
    """
    session = Session.query.get(id)
    
    if not session:
        return make_response(jsonify({'error': 'Session not found'}), 404)
    
    speakers_list = [
        {
            'id': speaker.id,
            'name': speaker.name,
            'bio_text': speaker.bio.bio_text if speaker.bio else 'No bio available'
        }
        for speaker in session.speakers
    ]
    return make_response(jsonify(speakers_list), 200)


# ==================== Main ====================

if __name__ == '__main__':
    app.run(port=5555, debug=True)