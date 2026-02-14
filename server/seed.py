"""
Seed script to populate the EventWise database with sample data
"""
from datetime import datetime
from app import app
from models import db, Event, Session, Speaker, Bio

def seed_database():
    """Populate database with sample events, sessions, speakers, and bios"""
    with app.app_context():
        # Clear existing data
        print("Clearing existing data...")
        db.drop_all()
        db.create_all()

        # Create Events
        print("Creating events...")
        event1 = Event(
            name="Tech Summit 2024",
            location="San Francisco, CA"
        )
        event2 = Event(
            name="Developer Conference",
            location="Austin, TX"
        )
        event3 = Event(
            name="AI Symposium",
            location="New York, NY"
        )

        db.session.add_all([event1, event2, event3])
        db.session.commit()

        # Create Speakers
        print("Creating speakers...")
        speaker1 = Speaker(name="Dr. Jane Smith")
        speaker2 = Speaker(name="John Doe")
        speaker3 = Speaker(name="Alice Johnson")
        speaker4 = Speaker(name="Bob Williams")

        db.session.add_all([speaker1, speaker2, speaker3, speaker4])
        db.session.commit()

        # Create Bios (some speakers have bios, some don't)
        print("Creating bios...")
        bio1 = Bio(
            bio_text="Dr. Jane Smith is a renowned AI researcher with 15 years of experience in machine learning.",
            speaker_id=speaker1.id
        )
        bio2 = Bio(
            bio_text="John Doe is a full-stack developer and tech entrepreneur.",
            speaker_id=speaker2.id
        )
        bio3 = Bio(
            bio_text="Alice Johnson specializes in cloud architecture and DevOps practices.",
            speaker_id=speaker3.id
        )
        # Note: speaker4 (Bob Williams) has no bio

        db.session.add_all([bio1, bio2, bio3])
        db.session.commit()

        # Create Sessions
        print("Creating sessions...")
        session1 = Session(
            title="Introduction to Machine Learning",
            start_time=datetime(2024, 6, 15, 9, 0),
            event_id=event1.id
        )
        session2 = Session(
            title="Advanced Neural Networks",
            start_time=datetime(2024, 6, 15, 14, 0),
            event_id=event1.id
        )
        session3 = Session(
            title="Building Scalable Web Apps",
            start_time=datetime(2024, 7, 20, 10, 0),
            event_id=event2.id
        )
        session4 = Session(
            title="Cloud Infrastructure Best Practices",
            start_time=datetime(2024, 7, 20, 15, 30),
            event_id=event2.id
        )
        session5 = Session(
            title="The Future of AI",
            start_time=datetime(2024, 8, 10, 11, 0),
            event_id=event3.id
        )

        db.session.add_all([session1, session2, session3, session4, session5])
        db.session.commit()

        # Associate Speakers with Sessions (many-to-many)
        print("Associating speakers with sessions...")
        session1.speakers.append(speaker1)  # Dr. Jane Smith
        session1.speakers.append(speaker2)  # John Doe

        session2.speakers.append(speaker1)  # Dr. Jane Smith

        session3.speakers.append(speaker2)  # John Doe
        session3.speakers.append(speaker3)  # Alice Johnson

        session4.speakers.append(speaker3)  # Alice Johnson

        session5.speakers.append(speaker1)  # Dr. Jane Smith
        session5.speakers.append(speaker4)  # Bob Williams (no bio)

        db.session.commit()

        print("✅ Database seeded successfully!")
        print(f"  - {Event.query.count()} events created")
        print(f"  - {Session.query.count()} sessions created")
        print(f"  - {Speaker.query.count()} speakers created")
        print(f"  - {Bio.query.count()} bios created")


if __name__ == '__main__':
    seed_database()