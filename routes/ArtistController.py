from models import Artist, Venue, db
from sqlalchemy import asc
from flask import (
   render_template,
   request,
   flash,
   redirect,
   url_for,
   Blueprint
)
from datetime import datetime
from forms import ArtistForm
import sys
import json

artist_blueprint = Blueprint('artists', __name__)

#  Artist
#  ----------------------------------------------------------------
class ArtistController():

    @artist_blueprint.route('/')
    def artists():
        query_data = Artist.query.all()
        data = []
        for item in query_data:
            data.append({
              "id": item.id,
              "name": item.name,
            })

        return render_template('pages/artists.html', artists=data)

    @artist_blueprint.route('/search', methods=['POST'])
    def search_artists():
        # implement search on artists with partial string search. Ensure it is case-insensitive.
        # search for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
        # search for "band" should return "The Wild Sax Band".
        term = request.form.get('search_term')
        term = "%{}%".format(term)
        query_data = Artist.query.filter(Artist.name.ilike(term)|Artist.city.ilike(term)|Artist.state.ilike(term)).all()
        data = []
        for item in query_data:
            data.append({
              "id": item.id,
              "name": item.name,
              "num_upcoming_shows": 0
            })
        response={
          "count": len(query_data),
          "data": data
        }
        return render_template('pages/search_artists.html',
                                results=response, search_term=request.form.get('search_term', ''))

    @artist_blueprint.route('/<int:artist_id>')
    def show_artist(artist_id):
        artist = Artist.query.filter_by(id=artist_id).first()
        past_shows = []
        upcoming_shows = []
        for show in artist.shows:
            show_data = {
                "artist_id": show.artist_id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            }
            if datetime.now() > show.start_time:
                past_shows.append(show_data)
            else:
                upcoming_shows.append(show_data)

        data = {
            "id": artist.id,
            "name": artist.name,
            "genres": artist.genres,
            "city": artist.city,
            "state": artist.state,
            "phone": artist.phone,
            "website": artist.website,
            "image_link": artist.image_link,
            "facebook_link": artist.facebook_link,
            "seeking_venue": artist.seeking_venue,
            "seeking_description": artist.seeking_description,
            "past_shows": past_shows,
            "past_shows_count": len(past_shows),
            "upcoming_shows": upcoming_shows,
            "upcoming_shows_count": len(upcoming_shows)
        }

        return render_template('pages/show_artist.html', artist=data)


    #  Create Artist
    #  ----------------------------------------------------------------

    @artist_blueprint.route('/create', methods=['GET'])
    def create_artist_form():
        form = ArtistForm()
        return render_template('forms/new_artist.html', form=form)

    @artist_blueprint.route('/create', methods=['POST'])
    def create_artist_submission():
        error= False
        # called upon submitting the new artist listing form
        # insert form data as a new Venue record in the db, instead
        # modify data to be the data object returned from db insertion
        try:
            name = request.form['name']
            city = request.form['city']
            state = request.form['state']
            genres = request.form.getlist('genres')
            phone = request.form['phone']
            image_link = request.form['image_link']
            facebook_link = request.form['facebook_link']
            website = request.form['website']
            seeking_venue = json.loads(request.form['seeking_venue'].lower())
            seeking_description = request.form['seeking_description']
            created_at = datetime.now()
            artist = Artist(name=name, city=city, state=state, phone=phone,
                        genres=genres,facebook_link=facebook_link, image_link=image_link,
                        website=website, seeking_venue=seeking_venue, seeking_description=seeking_description,
                        created_at=created_at)
            db.session.add(artist)
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
            flash('Artist ' + request.form['name'] + ' was successfully listed!')
        # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
        return render_template('pages/home.html')

    #  Update Artist
    #  ----------------------------------------------------------------
    @artist_blueprint.route('/<int:artist_id>/edit', methods=['GET'])
    def edit_artist(artist_id):
        form = ArtistForm()
        artist = Artist.query.filter_by(id=artist_id).first()

        form.seeking_venue.default = artist.seeking_venue
        form.process()

        form.name.data = artist.name
        form.city.data = artist.city
        form.state.data = artist.state
        form.genres.data = artist.genres
        form.phone.data = artist.phone
        form.website.data = artist.website
        form.facebook_link.data = artist.facebook_link
        form.image_link.data = artist.image_link
        form.seeking_description.data = artist.seeking_description

        return render_template('forms/edit_artist.html', form=form, artist=artist)

    @artist_blueprint.route('/<int:artist_id>/edit', methods=['POST'])
    def edit_artist_submission(artist_id):
        # take values from the form submitted, and update existing
        # artist record with ID <artist_id> using the new attributes
        artist = Artist.query.get(artist_id)
        error = False
        try:
            artist.name = request.form['name']
            artist.city = request.form['city']
            artist.state = request.form['state']
            artist.genres = request.form.getlist('genres')
            artist.phone = request.form['phone']
            artist.image_link = request.form['image_link']
            artist.facebook_link = request.form['facebook_link']
            artist.website = request.form['website']
            artist.seeking_venue = json.loads(request.form['seeking_venue'].lower())
            artist.seeking_description = request.form['seeking_description']

            db.session.commit()
        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
        # on successful db insert, flash success
        if error:
            flash('An error occurred.')
        if not error:
            flash('Artist ' + request.form['name'] + ' was successfully updated!')
        return redirect(url_for('artists.show_artist', artist_id=artist_id))


    @artist_blueprint.route('/<artist_id>', methods=['DELETE'])
    def delete_artist(artist_id):
        error=False
        try:
            artist = Artist.query.get(artist_id)
            # TODO: delete related shows before deleting the artist
            db.session.delete(artist)
            db.session.commit()
        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()

        if error:
            flash(f'An error occurred.')
        if not error:
            flash('Artist was successfully deleted.')

        return redirect(url_for('home.index'))
