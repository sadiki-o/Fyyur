"""empty message

Revision ID: e2b73e817b91
Revises: 100c07d5b4b0
Create Date: 2022-07-26 01:32:19.055116

"""
from alembic import op
from sqlalchemy import DDL, event
from models.Show import Show

# revision identifiers, used by Alembic.
revision = 'e2b73e817b91'
down_revision = '100c07d5b4b0'
branch_labels = None
depends_on = None


def upgrade():
    #code responsible for handling artists availability when creating a show
    conn = op.get_bind()
    availability_trigger = DDL('''
        CREATE OR REPLACE FUNCTION check_availability()
        RETURNS TRIGGER AS
        $func$
        BEGIN
        IF EXISTS (
        select * 
        from shows s
        where DATE_PART('day',NEW.start_time::date) = DATE_PART('day',s.start_time::date) 
        and DATE_PART('month',NEW.start_time::date) = DATE_PART('month',s.start_time::date) 
        and DATE_PART('year',NEW.start_time::date) = DATE_PART('year',s.start_time::date) 
        and NEW.artist_id = s.artist_id) THEN
        RAISE EXCEPTION 'The artist isnt available at that date';
        END IF;
        RETURN NEW;
        END
        $func$  LANGUAGE plpgsql;
        
        CREATE or replace TRIGGER trigger_availability
        BEFORE INSERT OR UPDATE 
        ON shows 
        FOR EACH ROW 
        EXECUTE PROCEDURE check_availability();

        ''')
    op.get_bind()
    conn.execute(availability_trigger)



def downgrade():
    pass
