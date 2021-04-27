from flask_sqlalchemy import SQLAlchemy
from datetime import datetime as dt
from copy import deepcopy

db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Shows(db.Model): # db.table also possible
    __tablename__ = "Shows"
    id = db.Column(db.Integer, primary_key = True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable = False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable = False)
    start_time = db.Column(db.DateTime, nullable=False) 

    def __repr__(self):
        return f"<Show {self.id} {self.date} {self.artist_id} {self.venue_id}"

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    website = db.Column(db.String(300))
    genres = db.Column(db.String(120), nullable=False)
    shows = db.relationship('Shows', backref = 'venue', cascade = 'all, delete-orphan', lazy = 'dynamic')

    def __repr__(self):
        return f"<Venue {self.id} {self.name}"

    # tODO: (DONE) implement any missing fields, as a database migration using Flask-Migrate

    @staticmethod
    def dictify_by_city_state(venue_lst):
        out = {}
        for venue in venue_lst:
            upcoming_shows = list(filter(lambda x: x.start_time>dt.now(),venue.shows.all()))
            data = {'id': venue.id, 'name': venue.name, 'num_upcoming_shows': len( upcoming_shows )}
            if (venue.city, venue.state) in out:
                out[(venue.city, venue.state)].append(deepcopy(data))
            else:
                out[(venue.city, venue.state)] = [deepcopy(data)]
        return [
              {"city": key[0],
              "state": key[1],
              "venues": venues} for key, venues in out.items() ]
        
            

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(500))
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Shows', backref = 'artist', cascade = 'all, delete-orphan', lazy = 'dynamic')

    def __repr__(self):
        return f"<Artist {self.id} {self.name}"
    # tODO: (DONE) implement any missing fields, as a database migration using Flask-Migrate

# tODO (DONE) Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
