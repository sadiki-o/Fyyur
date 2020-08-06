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
from forms import VenueForm
import sys
import json

venue_blueprint = Blueprint('venues', __name__)

#  Venue routes
#  ----------------------------------------------------------------
class VenueController():

    @venue_blueprint.route('/')
    def venues():
        all_cities = Venue.query.with_entities(Venue.city, Venue.state).distinct().all()
        data = []
        for item in all_cities:
            venues_list = []
            venues_query = Venue.query.filter_by(city=item.city).filter_by(state=item.state).all()
            for venue in venues_query:
                venues_list.append({
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcoming_shows": len([])
                })
            data.append({
                "city": item.city,
                "state": item.state,
                "venues": venues_list
            })

        return render_template('pages/venues.html', areas=data)

    @venue_blueprint.route('/search', methods=['POST'])
    def search_venues():
        term = request.form.get('search_term')
        term = "%{}%".format(term)
        query_data = Venue.query.filter(Venue.name.ilike(term) | Venue.city.ilike(term) | Venue.state.ilike(term)).all()
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
        print(response)
        return render_template('pages/search_venues.html',
                               results=response, search_term=request.form.get('search_term', ''))

    @venue_blueprint.route('/<int:venue_id>')
    def show_venue(venue_id):
        venue = Venue.query.filter_by(id=venue_id).first()
        past_shows = []
        upcoming_shows = []
        for show in venue.shows:
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
            "id": venue.id,
            "name": venue.name,
            "genres": venue.genres,
            "city": venue.city,
            "state": venue.state,
            "address": venue.address,
            "phone": venue.phone,
            "website": venue.website,
            "image_link": venue.image_link,
            "facebook_link": venue.facebook_link,
            "seeking_talent": venue.seeking_talent,
            "seeking_description": venue.seeking_description,
            "past_shows": past_shows,
            "past_shows_count": len(past_shows),
            "upcoming_shows": upcoming_shows,
            "upcoming_shows_count": len(upcoming_shows)
        }

        return render_template('pages/show_venue.html', venue=data)

    #  Create Venue
    #  ----------------------------------------------------------------

    @venue_blueprint.route('/create', methods=['GET'])
    def create_venue_form():
        form = VenueForm()
        return render_template('forms/new_venue.html', form=form)

    @venue_blueprint.route('/create', methods=['POST'])
    def create_venue_submission():
        error = False
        try:
            name = request.form['name']
            city = request.form['city']
            state = request.form['state']
            address = request.form['address']
            genres = request.form.getlist('genres')
            phone = request.form['phone']
            image_link = request.form['image_link']
            facebook_link = request.form['facebook_link']
            website = request.form['website']
            seeking_talent = bool(request.form['seeking_talent'])
            seeking_description = request.form['seeking_description']
            created_at = datetime.now()
            venue = Venue(name=name, city=city, state=state, address=address, phone=phone,
                        genres=genres,facebook_link=facebook_link, image_link=image_link,
                        website=website, seeking_talent=seeking_talent, seeking_description=seeking_description,
                        created_at=created_at)

            db.session.add(venue)
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
            flash('Venue ' + request.form['name'] + ' was successfully listed!')
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        return render_template('pages/home.html')


    #  Edit Venue
    #  ----------------------------------------------------------------
    @venue_blueprint.route('/<int:venue_id>/edit', methods=['GET'])
    def edit_venue(venue_id):
        form = VenueForm()
        venue = Venue.query.filter_by(id=venue_id).first()

        form.seeking_talent.default = venue.seeking_talent
        form.process()

        form.name.data = venue.name
        form.city.data = venue.city
        form.state.data = venue.state
        form.genres.data = venue.genres
        form.address.data = venue.address
        form.phone.data = venue.phone
        form.website.data = venue.website
        form.facebook_link.data = venue.facebook_link
        form.image_link.data = venue.image_link
        form.seeking_description.data = venue.seeking_description

        return render_template('forms/edit_venue.html', form=form, venue=venue)

    @venue_blueprint.route('/<int:venue_id>/edit', methods=['POST'])
    def edit_venue_submission(venue_id):
        # take values from the form submitted, and update existing
        # venue record with ID <venue_id> using the new attributes
        venue = Venue.query.get(venue_id)
        error = False
        try:
            venue.name = request.form['name']
            venue.city = request.form['city']
            venue.state = request.form['state']
            venue.address = request.form['address']
            venue.genres = request.form.getlist('genres')
            venue.phone = request.form['phone']
            venue.image_link = request.form['image_link']
            venue.facebook_link = request.form['facebook_link']
            venue.website = request.form['website']
            venue.seeking_talent = json.loads(request.form['seeking_talent'].lower())
            venue.seeking_description = request.form['seeking_description']

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
            flash('Venue ' + request.form['name'] + ' was successfully listed!')
        return redirect(url_for('venues.show_venue', venue_id=venue_id))


    #  Delete Venue
    #  ----------------------------------------------------------------

    @venue_blueprint.route('/<venue_id>', methods=['DELETE'])
    def delete_venue(venue_id):
        error=False
        try:
            venue = Venue.query.get(venue_id)
            # TODO: delete related shows before deleting the venue
            db.session.delete(venue)
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
            flash('Venue was successfully deleted.')

        return redirect(url_for('home.index'))