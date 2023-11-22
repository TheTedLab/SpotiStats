from detail.entity.city import City
from detail.entity.genre import Genre
from detail.entity.track import Track

class Artist:

    TABLE_NAME = 'artist'
    TABLE_NAME__CITY = 'artist__city'
    TABLE_NAME__GENRE = 'artist__genre'
    TABLE_NAME__TRACK = 'artist__track'

    def __init__(self, id, spotify_id, name, followers, popularity, monthly_listeners = None, world_rank = None):
        self.id = id
        self.spotify_id = spotify_id
        self.name = name
        self.followers = followers
        self.popularity = popularity
        self.monthly_listeners = monthly_listeners
        self.world_rank = world_rank

        self.genres = None

    @staticmethod
    def save(conn, spotify_id, name, followers, popularity, monthly_listeners = None, world_rank = None):
        try:
            with conn.cursor() as cur:
                cur.execute(f'''
                        INSERT INTO {Artist.TABLE_NAME} (spotify_id, name, followers, popularity, monthly_listeners, world_rank)
                        VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (spotify_id) DO UPDATE
                        SET (spotify_id, name, followers, popularity, monthly_listeners, world_rank) =
                            (EXCLUDED.spotify_id, EXCLUDED.name, EXCLUDED.followers, EXCLUDED.popularity, EXCLUDED.monthly_listeners, EXCLUDED.world_rank)
                    ''', spotify_id, name, followers, popularity, monthly_listeners, world_rank)
                return True
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def update(conn, spotify_id, followers = None, popularity = None, monthly_listeners = None, world_rank = None):
        try:
            with conn.cursor() as cur:
                cur.execute(f'''
                        UPDATE {Artist.TABLE_NAME} SET
                          followers = COALESCE(%s, followers),
                          popularity = COALESCE(%s, popularity),
                          monthly_listeners = COALESCE(%s, monthly_listeners),
                          world_rank = COALESCE(%s, world_rank)
                        WHERE spotify_id = %s
                    ''', followers, popularity, monthly_listeners, world_rank, spotify_id)
                return True
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def get_by_id(conn, id):
        if not id: return None

        with conn.cursor() as cur:
            cur.execute(f'''
                    SELECT spotify_id, name, followers, popularity, monthly_listeners, world_rank
                    FROM {Artist.TABLE_NAME} WHERE id = %s
                ''', id)
            result = cur.fetchone()

        if not result: return None

        return Artist(id, *result)

    def get_cities(self, conn):
        with conn.cursor() as cur:
            cur.execute(f'''
                    SELECT
                        {City.TABLE_NAME}.id,
                        {City.TABLE_NAME}.name,
                        {City.TABLE_NAME}.country,
                        {City.TABLE_NAME}.region
                    FROM {Artist.TABLE_NAME__CITY}
                    JOIN {City.TABLE_NAME} ON {Artist.TABLE_NAME__CITY}.city_id = {City.TABLE_NAME}.id
                    WHERE {Artist.TABLE_NAME__CITY}.artist_id = %s
                ''', self.id)
            result = [City(*entry) for entry in cur.fetchall()]

        return result

    def get_genres(self, conn):
        with conn.cursor() as cur:
            cur.execute(f'''
                    SELECT {Genre.TABLE_NAME}.id, {Genre.TABLE_NAME}.name
                    FROM {Artist.TABLE_NAME__GENRE}
                    JOIN {Genre.TABLE_NAME} ON {Artist.TABLE_NAME__GENRE}.genre_id = {Genre.TABLE_NAME}.id
                    WHERE {Artist.TABLE_NAME__GENRE}.artist_id = %s
                ''', self.id)
            result = [Genre(*entry) for entry in cur.fetchall()]

        return result

    def get_tracks(self, conn):
        with conn.cursor() as cur:
            cur.execute(f'''
                    SELECT
                        {Track.TABLE_NAME}.id,
                        {Track.TABLE_NAME}.spotify_id,
                        {Track.TABLE_NAME}.name,
                        {Track.TABLE_NAME}.duration_ms,
                        {Track.TABLE_NAME}.explicit,
                        {Track.TABLE_NAME}.popularity,
                        {Track.TABLE_NAME}.features,
                        {Track.TABLE_NAME}.plays
                    FROM {Artist.TABLE_NAME__TRACK}
                    JOIN {Track.TABLE_NAME} ON {Artist.TABLE_NAME__TRACK}.track_id = {Track.TABLE_NAME}.id
                    WHERE {Artist.TABLE_NAME__TRACK}.artist_id = %s
                ''', self.id)
            result = [Track(*entry) for entry in cur.fetchall()]

        return result