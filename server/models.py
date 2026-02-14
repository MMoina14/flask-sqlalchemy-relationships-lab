"""
EventWise Database Models
Defines Event, Session, Speaker, and Bio models with appropriate relationships
"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

# Define naming convention for constraints
metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)


# Association table for many-to-many relationship between Session and Speaker
session_speakers = db.Table(
    'session_speakers',
    db.Column('session_id', db.Integer, db.ForeignKey('sessions.id'), primary_key=True),
    db.Column('speaker_id', db.Integer, db.ForeignKey('speakers.id'), primary_key=True)
)


class Event(db.Model):
    """
    Event model representing an event that can have multiple sessions
    One-to-Many relationship with Session
    """
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)

    # One-to-Many: Event has many Sessions
    # cascade='all, delete-orphan' ensures sessions are deleted when event is deleted
    sessions = db.relationship(
        'Session',
        back_populates='event',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<Event {self.id}: {self.name} at {self.location}>'


class Session(db.Model):
    """
    Session model representing a session belonging to an event
    Many-to-One relationship with Event
    Many-to-Many relationship with Speaker
    """
    __tablename__ = 'sessions'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)

    # Many-to-One: Session belongs to Event
    event = db.relationship('Event', back_populates='sessions')

    # Many-to-Many: Session has many Speakers through session_speakers
    speakers = db.relationship(
        'Speaker',
        secondary=session_speakers,
        back_populates='sessions'
    )

    def __repr__(self):
        return f'<Session {self.id}: {self.title}>'


class Speaker(db.Model):
    """
    Speaker model representing a speaker who can participate in multiple sessions
    One-to-One relationship with Bio
    Many-to-Many relationship with Session
    """
    __tablename__ = 'speakers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    # One-to-One: Speaker has one Bio
    # cascade='all, delete-orphan' ensures bio is deleted when speaker is deleted
    # uselist=False makes this a one-to-one relationship
    bio = db.relationship(
        'Bio',
        back_populates='speaker',
        cascade='all, delete-orphan',
        uselist=False
    )

    # Many-to-Many: Speaker has many Sessions through session_speakers
    sessions = db.relationship(
        'Session',
        secondary=session_speakers,
        back_populates='speakers'
    )

    def __repr__(self):
        return f'<Speaker {self.id}: {self.name}>'


class Bio(db.Model):
    """
    Bio model representing a speaker's biography
    One-to-One relationship with Speaker
    """
    __tablename__ = 'bios'

    id = db.Column(db.Integer, primary_key=True)
    bio_text = db.Column(db.String, nullable=False)
    speaker_id = db.Column(db.Integer, db.ForeignKey('speakers.id'), nullable=False, unique=True)

    # One-to-One: Bio belongs to Speaker
    speaker = db.relationship('Speaker', back_populates='bio')

    def __repr__(self):
        return f'<Bio {self.id} for Speaker {self.speaker_id}>'