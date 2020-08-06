from models import Artist, Venue, Show, db
from sqlalchemy import asc
from flask import (
   render_template,
   request,
   flash,
   url_for,
   Blueprint
)
from datetime import datetime
from forms import ShowForm
import sys
import json

show_blueprint = Blueprint('shows', __name__)

#  Show routes
#  ----------------------------------------------------------------
class ShowController():
    @show_blueprint.route('/')
    def shows():
        # displays list of shows at /shows
        query_data = Show.query.all()
        data = []
        for item in query_data:
            data.append({
              "venue_id": item.venue_id,
              "venue_name": item.venue.name,
              "artist_id": item.artist_id,
              "artist_name": item.artist.name,
              "artist_image_link": item.artist.image_link,
              "start_time": item.start_time.strftime('%Y-%m-%d %H:%M:%S')
            })
        return render_template('pages/shows.html', shows=data)

    @show_blueprint.route('/create')
    def create_shows():
        form = ShowForm()
        return render_template('forms/new_show.html', form=form)

    @show_blueprint.route('/create', methods=['POST'])
    def create_show_submission():
        error = False
        # called to create new shows in the db, upon submitting new show listing form
        # insert form data as a new Show record in the db, instead
        try:
            artist_id = request.form['artist_id']
            venue_id = request.form['venue_id']
            start_time = request.form['start_time']
            show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
            db.session.add(show)
            db.session.commit()
        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()

        if error:
            # on unsuccessful db insert, flash an error.
            flash('An error occurred.')
        if not error:
            # on successful db insert, flash success
            flash('Show was successfully listed!')
        # e.g., flash('An error occurred. Show could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        return render_template('pages/home.html')