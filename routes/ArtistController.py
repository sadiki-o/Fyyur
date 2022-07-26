from flask import Blueprint, flash, render_template, request, url_for, redirect
from forms import ArtistForm
from models.Artist import Artist
import sys
from datetime import datetime
from models.db_file import db
from models.Show import Show
from models.Venue import Venue
from sqlalchemy import func

artist_bp = Blueprint('artists', __name__)


class ArtistController:

    #  Get Artists
    #  ----------------------------------------------------------------
    @artist_bp.route('/')
    def artists():
        try:
            data = Artist.query.all()
            return render_template('pages/artists.html', artists=data)
        except:
            return render_template('pages/artists.html', error="Error while loading")

    #  Search Artist
    #  ----------------------------------------------------------------
    @artist_bp.route('/search', methods=['POST'])
    def search_artists():
        s = F"%{request.form.get('search_term')}%"
        data = Artist.query.filter(Artist.name.ilike(s) | Artist.city.ilike(s) | Artist.state.ilike(s)).all()
        response = {
            "count": len(data),
            "data": data
        }
        return render_template('pages/search_artists.html', results=response,
                               search_term=request.form.get('search_term', ''))

    #  Get Artist Details
    #  ----------------------------------------------------------------
    @artist_bp.route('/<int:artist_id>')
    def show_artist(artist_id):
        a = Artist.query.get(artist_id)
        upcoming_shows = []
        past_shows = []

        past_shows_query = db.session.query(Show.start_time, Venue.id, Venue.name, Venue.image_link).join(Venue).filter(Show.artist_id == artist_id).filter(
            Show.start_time < datetime.now()).all()
        print(past_shows_query)
        for show in past_shows_query:
            past_shows.append({
                "venue_id": show.id,
                "venue_name": show.name,
                "venue_image_link": show.image_link,
                "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            })

        upcoming_shows_query = db.session.query(Show.start_time, Venue.id, Venue.name, Venue.image_link).join(Venue).filter(Show.artist_id == artist_id).filter(
            Show.start_time > datetime.now()).all()

        for show in upcoming_shows_query:
            upcoming_shows.append({
                "artist_id": show.id,
                "artist_name": show.name,
                "artist_image_link": show.image_link,
                "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            })

        final_artist = {
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "id": a.id,
            "name": a.name,
            "genres": a.genres,
            "city": a.city,
            "state": a.state,
            "phone": a.phone,
            "website": a.website,
            "image_link": a.image_link,
            "facebook_link": a.facebook_link,
            "seeking_venue": a.seeking_venue,
            "seeking_description": a.seeking_description,
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcoming_shows)
        }
        return render_template('pages/show_artist.html', artist=final_artist)

    #  Update Artist
    #  ----------------------------------------------------------------
    @artist_bp.route('/<int:artist_id>/edit', methods=['GET'])
    def edit_artist(artist_id):
        artist = Artist.query.get(artist_id)
        form = ArtistForm(obj=artist)
        return render_template('forms/edit_artist.html', form=form, artist=artist)

    @artist_bp.route('/<int:artist_id>/edit', methods=['POST'])
    def edit_artist_submission(artist_id):
        form = ArtistForm()
        artist = Artist.query.get(artist_id)
        if not form.validate_on_submit():
            print(form.errors)
            sep = '\n'
            return render_template('forms/edit_artist.html', artist=artist , form=form)
        try:

            artist.name = request.form['name']
            artist.city = request.form['city']
            artist.state = request.form['state']
            artist.genres = request.form.getlist('genres')
            artist.phone = request.form['phone']
            artist.image_link = request.form['image_link']
            artist.facebook_link = request.form['facebook_link']
            artist.website = request.form['website']
            artist.seeking_venue = True if request.form.get("seeking_venue") is not None else False
            artist.seeking_description = request.form['seeking_description']
            artist.created_at = datetime.now()
            db.session.commit()

            data = Artist.query.all()
            flash(F"{artist.name} was updated successfully")
            return render_template('pages/artists.html', artists=data)
        except:
            db.session.rollback()
            print(sys.exc_info())
            return render_template('forms/edit_artist.html', artist=artist , form=form, error="Update was unsuccessful")
        finally:
            db.session.close()

    #  Create Artist
    #  ----------------------------------------------------------------

    @artist_bp.route('/create', methods=['GET'])
    def create_artist_form():
        form = ArtistForm()
        return render_template('forms/new_artist.html', form=form)

    @artist_bp.route('/create', methods=['POST'])
    def create_artist_submission():
        form = ArtistForm()

        if not form.validate_on_submit():
            print(form.errors)
            sep = '\n'
            return render_template('forms/new_artist.html', form=form)
        data = Artist.query.all()
        try:
            name = request.form['name']
            city = request.form['city']
            state = request.form['state']
            genres = request.form.getlist('genres')
            phone = request.form['phone']
            image_link = request.form['image_link']
            facebook_link = request.form['facebook_link']
            website = request.form['website']
            seeking_venue = True if request.form.get("seeking_venue") is not None else False
            seeking_description = request.form['seeking_description']
            created_at = datetime.now()

            new_artist = Artist(name=name, city=city, state=state, phone=phone,
                                genres=genres, facebook_link=facebook_link, image_link=image_link,
                                website=website, seeking_venue=seeking_venue,
                                seeking_description=seeking_description,
                                created_at=created_at)
            db.session.add(new_artist)
            db.session.commit()
            data = Artist.query.all()
            flash('Artist was successfully added')
            return render_template('pages/artists.html', artists=data)
        except:
            db.session.rollback()
            print(sys.exc_info())
            return render_template('pages/artists.html', error="Create was unsuccessful", artists=data)
        finally:
            db.session.close()

    #  Delete Artist
    #  ----------------------------------------------------------------
    @artist_bp.route('/delete', methods=['POST'])
    def delete_artist():
        try:
            artist_id = request.form['id']
            artist = Artist.query.get(artist_id)
            db.session.delete(artist)
            db.session.commit()
            flash(F'Artist {artist.name} was successfully deleted.')
            data = Artist.query.all()
            return render_template("pages/artists.html", artists=data)
        except:
            db.session.rollback()
            print(sys.exc_info())
            return render_template("pages/artists.html", error="Unexpected error while deleting")
        finally:
            db.session.close()
