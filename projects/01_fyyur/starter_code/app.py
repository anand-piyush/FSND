#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import logging
import traceback
from forms import *
from datetime import datetime as dt
from flask_moment import Moment
from flask_migrate import Migrate
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from logging import Formatter, FileHandler
from flask_wtf import Form
from copy import deepcopy
from models import db, Shows, Artist, Venue

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

# initialisation of migration 
migrate = Migrate(app, db)

# tODO: (DONE) connect to a local postgresql database

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # tODO: (DONE) replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  # sample data
  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]
  venues = Venue.query.all()
  data = Venue.dictify_by_city_state(venues)
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # tODO: (Done) implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  # sample data
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  search_term = request.form.get('search_term', "")
  venues = Venue.query.filter(
  Venue.name.ilike("%{}%".format(search_term))).all()
  data = [ {
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": len(list(filter(
        lambda show: show.start_time>dt.now(),venue.shows.all()
      )))
  }
  for venue in venues]
  response={
    "count": len(venues),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # tODO: (Done) replace with real venue data from the venues table, using venue_id

  # venue get basis id
  # it has shows, time and ids
  # uske basis par i will bucketise into past and upcoming
  # and artist name and image link also add
  # sample data
  # data1={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #   "past_shows": [{
  #     "artist_id": 4,
  #     "artist_name": "Guns N Petals",
  #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  
  venue = Venue.query.get(venue_id)
  data = venue.__dict__
  data["genres"] = venue.genres.split(',')
  data["past_shows"] = []
  data["upcoming_shows"] = []
  shows = venue.shows.all()
  for show in shows:
    artist = Artist.query.get(show.artist_id)
    show_details = {
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": show.start_time.isoformat()
    }
    if show.start_time>dt.now():
      data["upcoming_shows"].append(deepcopy(show_details))
    else:
      data["past_shows"].append(deepcopy(show_details))
  data["upcoming_shows_count"]=len(data["upcoming_shows"])
  data["past_shows_count"]=len(data["past_shows"])
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # tODO: (Done) insert form data as a new Venue record in the db, instead
    # tODO: (Done) modify data to be the data object returned from db insertion
    venue_form = VenueForm(request.form)
    try:
      new_venue = Venue(
          name=venue_form.name.data,
          genres=','.join(venue_form.genres.data),
          address=venue_form.address.data,
          city=venue_form.city.data,
          state=venue_form.state.data,
          phone=venue_form.phone.data,
          facebook_link=venue_form.facebook_link.data,
          image_link=venue_form.image_link.data,
          seeking_talent = venue_form.seeking_talent.data,
          seeking_description = venue_form.seeking_description.data,
          website = venue_form.website_link.data
          )

      db.session.add(new_venue)
      db.session.commit()
      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except Exception as e:
        # tODO: (Done) on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        flash('Error!. Venue ' +
              request.form['name'] + ' could not be listed.')
        db.session.rollback()
        traceback.print_exc()
    finally:
      db.session.close()
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # tODO: (Done) Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  # BONUS CHALLENGE:  (Done) Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  try:
    print(venue_id)
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return jsonify({'success': True})
  

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # tODO: (Done) replace with real data returned from querying the database
  # sample data
  # data=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }, {
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  # }]
  data = [ {'id':artist.id, 'name': artist.name }for artist in Artist.query.all()]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # tODO: (Done) implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  # sample data
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  search_term = request.form.get('search_term', "")
  artists = Artist.query.filter(
  Artist.name.ilike("%{}%".format(search_term))).all()
  data = [ {
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": len(list(filter(
        lambda show: show.start_time>dt.now(),artist.shows.all()
      )))
  }
  for artist in artists]
  response={
    "count": len(artists),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # tODO: (Done) replace with real artist data from the artist table, using artist_id
  # sample data
  # data1={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "past_shows": [{
  #     "venue_id": 1,
  #     "venue_name": "The Musical Hop",
  #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  artist = Artist.query.get(artist_id)
  data = artist.__dict__
  data["genres"] = artist.genres.split(',')
  data["past_shows"] = []
  data["upcoming_shows"] = []
  shows = artist.shows.all()
  for show in shows:
    venue = Venue.query.get(show.venue_id)
    show_details = {
      "venue_id": venue.id,
      "venue_name": venue.name,
      "venue_image_link": venue.image_link,
      "start_time": show.start_time.isoformat()
    }
    if show.start_time>dt.now():
      data["upcoming_shows"].append(deepcopy(show_details))
    else:
      data["past_shows"].append(deepcopy(show_details))
  data["upcoming_shows_count"]=len(data["upcoming_shows"])
  data["past_shows_count"]=len(data["past_shows"])
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # tODO: (Done) populate form with fields from artist with ID <artist_id>
  # sample data
  # artist={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  # }
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  data = artist.__dict__
  data["genres"] = artist.genres.split(',')
  
  return render_template('forms/edit_artist.html', form=form, artist=data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # tODO: (Done) take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
      artist_form = ArtistForm(request.form)
      artist = Artist.query.get(artist_id)
      artist.name=artist_form.name.data
      artist.genres=','.join(artist_form.genres.data)
      artist.city=artist_form.city.data
      artist.state=artist_form.state.data
      artist.phone=artist_form.phone.data
      artist.facebook_link=artist_form.facebook_link.data
      artist.image_link=artist_form.image_link.data
      artist.seeking_venue = artist_form.seeking_venue.data
      artist.seeking_description = artist_form.seeking_description.data
      artist.website = artist_form.website_link.data
      db.session.commit()
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully updated!')
  except Exception as e:
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('Error!. Artist ' +
          request.form['name'] + ' could not be updated.')
    db.session.rollback()
    traceback.print_exc()
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # tODO: (Done) populate form with values from venue with ID <venue_id>
  # sample data
  # venue={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  # }
  
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  data = venue.__dict__
  data["genres"] = venue.genres.split(',')
  return render_template('forms/edit_venue.html', form=form, venue=data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # tODO: (done) take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
      venue_form = VenueForm(request.form)
      venue = Venue.query.get(venue_id)
      venue.name = venue_form.name.data
      venue.genres = ','.join(venue_form.genres.data)
      venue.address = venue_form.address.data
      venue.city = venue_form.city.data
      venue.state = venue_form.state.data
      venue.phone = venue_form.phone.data
      venue.facebook_link = venue_form.facebook_link.data
      venue.image_link = venue_form.image_link.data
      venue.seeking_talent = venue_form.seeking_talent.data
      venue.seeking_description = venue_form.seeking_description.data
      venue.website = venue_form.website_link.data
      db.session.commit()
      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully updated!')
  except Exception as e:
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('Error!. Venue ' +
          request.form['name'] + ' could not be updated.')
    db.session.rollback()
    traceback.print_exc()
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # tODO: (Done) insert form data as a new Venue record in the db, instead
  # tODO: (Done) modify data to be the data object returned from db insertion
  artist_form = ArtistForm(request.form)
  try:
    new_artist = Artist(
        name=artist_form.name.data,
        genres=','.join(artist_form.genres.data),
        city=artist_form.city.data,
        state=artist_form.state.data,
        phone=artist_form.phone.data,
        facebook_link=artist_form.facebook_link.data,
        image_link=artist_form.image_link.data,
        seeking_venue = artist_form.seeking_venue.data,
        seeking_description = artist_form.seeking_description.data,
        website = artist_form.website_link.data
        )
    db.session.add(new_artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except Exception as e:
      # tODO: (Done) on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
      flash('Error!. Artist ' +
            request.form['name'] + ' could not be listed.')
      db.session.rollback()
      traceback.print_exc()
  finally:
    db.session.close()
  # on successful db insert, flash success
  # flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # tODO: (Done) on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')



#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # tODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  # sample data
  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   ....}]
  shows = Shows.query.all()
  data = [{
    "venue_id": show.venue_id,
    "venue_name": show.venue.name,
    "artist_id": show.artist_id,
    "artist_name": show.artist.name,
    "artist_image_link": show.artist.image_link,
    "start_time": show.start_time.isoformat()
  }for show in shows]

  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # tODO: (Done) insert form data as a new Show record in the db, instead
  show_form = ShowForm(request.form)
  try:
      show = Shows(
          artist_id=show_form.artist_id.data,
          venue_id=show_form.venue_id.data,
          start_time=show_form.start_time.data
      )
      db.session.add(show)
      db.session.commit()
      # on successful db insert, flash success
      flash('Show was successfully listed!')
  except Exception as e:
      # tODO: (Done) on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Show could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
      flash('An error occurred. Show could not be listed.')
      db.session.rollback()
      traceback.print_exc()
  finally:
      db.session.close()
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# TODO
# standout options
# final test, send and bring back comments


# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
