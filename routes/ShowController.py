from flask import Blueprint, flash, render_template, request
from forms import ShowForm
from models.Show import Show
from models.db_file import db
import sys
import time

show_bp = Blueprint('shows', __name__)


class ShowController:

    #  Get All Shows
    #  ----------------------------------------------------------------
    @show_bp.route('/')
    def shows():  # displays list of shows at /shows
        try:
            data = Show.query.all()
            formatted_data = []
            for show in data:
                formatted_data.append({
                    "artist_id": show.artist_id,
                    "venue_id": show.venue_id,
                    "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                    "artist_name": show.artist.name,
                    "venue_name": show.venue.name
                })
            return render_template('pages/shows.html', shows=formatted_data)
        except:
            print(sys.exc_info())
            return render_template('pages/shows.html', error="Error while loading")

    #  Create Show
    #  ----------------------------------------------------------------
    @show_bp.route('/create')
    def create_shows():
        form = ShowForm()
        return render_template('forms/new_show.html', form=form)

    @show_bp.route('/create', methods=['POST'])
    def create_show_submission():
        form = ShowForm()

        if not form.validate_on_submit():
            return render_template('forms/new_show.html', error='Please validate form', form=form)

        try:
            artist_id = request.form['artist_id']
            venue_id = request.form['venue_id']
            start_time = request.form['start_time']
            show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
            db.session.add(show)
            db.session.commit()
            flash('Show was successfully listed!')
            return render_template('pages/shows.html')
        except:
            db.session.rollback()
            print(sys.exc_info())
            return render_template('forms/new_show.html', error="Insert was unsuccessful", form=form)
        finally:
            db.session.close()
