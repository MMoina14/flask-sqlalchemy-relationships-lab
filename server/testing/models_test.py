"""
Test suite for EventWise Flask application
Tests models, relationships, and API endpoints
"""
import pytest
from datetime import datetime
from app import app
from models import db, Event, Session, Speaker, Bio


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            seed_test_data()
        yield client
        with app.app_context():
            db.session.remove()
            db.drop_all()


def seed_test_data():
    """Seed the test database with sample data"""
    # Create events
    event1 = Event(name="Tech Summit", location="San Francisco")
    event2 = Event(name="Dev Conference", location="Austin")
    db.session.add_all([event1, event2])
    db.session.commit()

    # Create speakers
    speaker1 = Speaker(name="Jane Smith")
    speaker2 = Speaker(name="John Doe")
    speaker3 = Speaker(name="Alice Johnson")
    db.session.add_all([speaker1, speaker2, speaker3])
    db.session.commit()

    # Create bios
    bio1 = Bio(bio_text="Jane is an AI expert", speaker_id=speaker1.id)
    bio2 = Bio(bio_text="John is a developer", speaker_id=speaker2.id)
    # speaker3 has no bio
    db.session.add_all([bio1, bio2])
    db.session.commit()

    # Create sessions
    session1 = Session(
        title="ML Basics",
        start_time=datetime(2024, 6, 15, 9, 0),
        event_id=event1.id
    )
    session2 = Session(
        title="Advanced ML",
        start_time=datetime(2024, 6, 15, 14, 0),
        event_id=event1.id
    )
    session3 = Session(
        title="Web Development",
        start_time=datetime(2024, 7, 20, 10, 0),
        event_id=event2.id
    )
    db.session.add_all([session1, session2, session3])
    db.session.commit()

    # Associate speakers with sessions
    session1.speakers.extend([speaker1, speaker2])
    session2.speakers.append(speaker1)
    session3.speakers.extend([speaker2, speaker3])
    db.session.commit()


# ==================== Model Tests ====================

class TestModels:
    """Test suite for database models"""

    def test_event_model(self, client):
        """Test Event model creation and attributes"""
        with app.app_context():
            event = Event.query.first()
            assert event is not None
            assert event.name == "Tech Summit"
            assert event.location == "San Francisco"

    def test_session_model(self, client):
        """Test Session model creation and attributes"""
        with app.app_context():
            session = Session.query.first()
            assert session is not None
            assert session.title == "ML Basics"
            assert session.event_id is not None

    def test_speaker_model(self, client):
        """Test Speaker model creation and attributes"""
        with app.app_context():
            speaker = Speaker.query.first()
            assert speaker is not None
            assert speaker.name == "Jane Smith"

    def test_bio_model(self, client):
        """Test Bio model creation and attributes"""
        with app.app_context():
            bio = Bio.query.first()
            assert bio is not None
            assert bio.bio_text == "Jane is an AI expert"
            assert bio.speaker_id is not None


# ==================== Relationship Tests ====================

class TestRelationships:
    """Test suite for model relationships"""

    def test_event_sessions_relationship(self, client):
        """Test one-to-many relationship: Event has many Sessions"""
        with app.app_context():
            event = Event.query.first()
            assert len(event.sessions) > 0
            assert all(isinstance(s, Session) for s in event.sessions)

    def test_session_event_relationship(self, client):
        """Test many-to-one relationship: Session belongs to Event"""
        with app.app_context():
            session = Session.query.first()
            assert session.event is not None
            assert isinstance(session.event, Event)

    def test_speaker_bio_relationship(self, client):
        """Test one-to-one relationship: Speaker has one Bio"""
        with app.app_context():
            speaker = Speaker.query.filter_by(name="Jane Smith").first()
            assert speaker.bio is not None
            assert isinstance(speaker.bio, Bio)
            assert speaker.bio.bio_text == "Jane is an AI expert"

    def test_bio_speaker_relationship(self, client):
        """Test one-to-one relationship: Bio belongs to Speaker"""
        with app.app_context():
            bio = Bio.query.first()
            assert bio.speaker is not None
            assert isinstance(bio.speaker, Speaker)

    def test_session_speakers_relationship(self, client):
        """Test many-to-many relationship: Session has many Speakers"""
        with app.app_context():
            session = Session.query.first()
            assert len(session.speakers) > 0
            assert all(isinstance(s, Speaker) for s in session.speakers)

    def test_speaker_sessions_relationship(self, client):
        """Test many-to-many relationship: Speaker has many Sessions"""
        with app.app_context():
            speaker = Speaker.query.first()
            assert len(speaker.sessions) > 0
            assert all(isinstance(s, Session) for s in speaker.sessions)

    def test_event_cascade_delete(self, client):
        """Test cascade delete: deleting Event deletes its Sessions"""
        with app.app_context():
            event = Event.query.first()
            event_id = event.id
            session_count_before = Session.query.filter_by(event_id=event_id).count()
            assert session_count_before > 0
            
            db.session.delete(event)
            db.session.commit()
            
            session_count_after = Session.query.filter_by(event_id=event_id).count()
            assert session_count_after == 0

    def test_speaker_cascade_delete(self, client):
        """Test cascade delete: deleting Speaker deletes their Bio"""
        with app.app_context():
            speaker = Speaker.query.filter_by(name="Jane Smith").first()
            speaker_id = speaker.id
            assert speaker.bio is not None
            
            db.session.delete(speaker)
            db.session.commit()
            
            bio = Bio.query.filter_by(speaker_id=speaker_id).first()
            assert bio is None


# ==================== Event Endpoint Tests ====================

class TestEventEndpoints:
    """Test suite for Event API endpoints"""

    def test_get_events(self, client):
        """Test GET /events endpoint"""
        response = client.get('/events')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert 'id' in data[0]
        assert 'name' in data[0]
        assert 'location' in data[0]

    def test_get_event_sessions_success(self, client):
        """Test GET /events/<id>/sessions with valid event"""
        response = client.get('/events/1/sessions')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert 'id' in data[0]
            assert 'title' in data[0]
            assert 'start_time' in data[0]

    def test_get_event_sessions_not_found(self, client):
        """Test GET /events/<id>/sessions with invalid event"""
        response = client.get('/events/9999/sessions')
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
        assert data['error'] == 'Event not found'


# ==================== Speaker Endpoint Tests ====================

class TestSpeakerEndpoints:
    """Test suite for Speaker API endpoints"""

    def test_get_speakers(self, client):
        """Test GET /speakers endpoint"""
        response = client.get('/speakers')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert 'id' in data[0]
        assert 'name' in data[0]

    def test_get_speaker_with_bio(self, client):
        """Test GET /speakers/<id> with speaker who has a bio"""
        response = client.get('/speakers/1')
        assert response.status_code == 200
        data = response.get_json()
        assert 'id' in data
        assert 'name' in data
        assert 'bio_text' in data
        assert data['bio_text'] != 'No bio available'

    def test_get_speaker_without_bio(self, client):
        """Test GET /speakers/<id> with speaker who has no bio"""
        response = client.get('/speakers/3')
        assert response.status_code == 200
        data = response.get_json()
        assert 'id' in data
        assert 'name' in data
        assert 'bio_text' in data
        assert data['bio_text'] == 'No bio available'

    def test_get_speaker_not_found(self, client):
        """Test GET /speakers/<id> with invalid speaker"""
        response = client.get('/speakers/9999')
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
        assert data['error'] == 'Speaker not found'


# ==================== Session Endpoint Tests ====================

class TestSessionEndpoints:
    """Test suite for Session API endpoints"""

    def test_get_session_speakers_success(self, client):
        """Test GET /sessions/<id>/speakers with valid session"""
        response = client.get('/sessions/1/speakers')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert 'id' in data[0]
        assert 'name' in data[0]
        assert 'bio_text' in data[0]

    def test_get_session_speakers_with_no_bio(self, client):
        """Test GET /sessions/<id>/speakers includes speakers without bios"""
        response = client.get('/sessions/3/speakers')
        assert response.status_code == 200
        data = response.get_json()
        # Check if any speaker has "No bio available"
        speakers_without_bio = [s for s in data if s['bio_text'] == 'No bio available']
        assert len(speakers_without_bio) > 0

    def test_get_session_speakers_not_found(self, client):
        """Test GET /sessions/<id>/speakers with invalid session"""
        response = client.get('/sessions/9999/speakers')
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
        assert data['error'] == 'Session not found' 