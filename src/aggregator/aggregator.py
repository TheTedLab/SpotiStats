import json
import time
import requests
from auth_credentials import client_id, client_secret, client_headers, client_extensions, token_type, access_token
from classes.artist import Artist
from classes.album import Album
from classes.track import Track

token_data = {
    'grant_type': 'client_credentials',
    'client_id': client_id,
    'client_secret': client_secret,
}


def main():
    timeout = 0.5

    request_count = 0

    headers = {
        'Authorization': f'{token_type}  {access_token}',
    }

    with open(f'resources/artists-ids-list.json', 'r', encoding='utf-8') as file:
        artists_ids = json.load(file)

    for artist_id in artists_ids[10392:10393]:
        # 1 request
        response = requests.get(
            f'https://api.spotify.com/v1/artists/{artist_id}',
            headers=headers
        )
        time.sleep(timeout)
        request_count += 1
        print(f"[Request {request_count} - {response.status_code}]")

        print(response.status_code)
        if response.status_code != 200:
            print('Token expired!')
            # 2 request (potential)
            response = requests.post(
                'https://accounts.spotify.com/api/token',
                data=token_data
            )
            time.sleep(timeout)
            request_count += 1
            print(f"[Request {request_count} - {response.status_code}]")

            headers['Authorization'] = f"{response.json().get('token_type')}  {response.json().get('access_token')}"

            # 3 request (potential)
            response = requests.get(
                f'https://api.spotify.com/v1/artists/{artist_id}',
                headers=headers
            )
            time.sleep(timeout)
            request_count += 1
            print(f"[Request {request_count} - {response.status_code}]")

        artist_info_data = response.json()
        print(f"Artist Name: {artist_info_data.get('name')}")
        print(f"Artist Popularity: {artist_info_data.get('popularity')}")
        print(f"Artist Genres: {artist_info_data.get('genres')}")
        print(f"Artist Followers: {artist_info_data.get('followers').get('total')}")

        artist_for_json = Artist(
            artist_id,
            artist_info_data.get('name'),
            artist_info_data.get('popularity'),
            artist_info_data.get('followers').get('total'),
            artist_info_data.get('genres'),
        )

        # client_params = {
        #     'operationName': 'queryArtistOverview',
        #     'variables': '{"uri":"spotify:artist:' + artist_id + '","locale":"","includePrerelease":true}',
        #     'extensions': client_extensions
        # }
        #
        # 4 request
        # response = requests.get(
        #     'https://api-partner.spotify.com/pathfinder/v1/query',
        #     params=client_params,
        #     headers=client_headers
        # )
        # time.sleep(timeout)
        # request_count += 1
        # print(f"[Request {request_count} - {response.status_code}]")
        #
        # artist_stats_data = response.json().get('data').get('artistUnion').get('stats')
        # print(f"Monthly Listeners: {artist_stats_data.get('monthlyListeners')}")
        # print(f"World Rank: {artist_stats_data.get('worldRank')}")
        # print(f"Cities: {artist_stats_data.get('topCities').get('items')}")
        # print()

        album_params = {
            'include_groups': 'album',
            'limit': 50,
            'offset': 0,
            'market': 'ES'
        }

        # 5 request
        response = requests.get(
            f'https://api.spotify.com/v1/artists/{artist_id}/albums',
            params=album_params,
            headers=headers
        )
        time.sleep(timeout)
        request_count += 1
        print(f"[Request {request_count} - {response.status_code}]")

        artist_albums_ids = list()
        artist_albums = response.json().get('items')
        for album in artist_albums:
            artist_albums_ids.append(album.get('id'))

        album_params['include_groups'] = 'single'

        # 6 request
        response = requests.get(
            f'https://api.spotify.com/v1/artists/{artist_id}/albums',
            params=album_params,
            headers=headers
        )
        time.sleep(timeout)
        request_count += 1
        print(f"[Request {request_count} - {response.status_code}]")

        artist_albums = response.json().get('items')
        for album in artist_albums:
            artist_albums_ids.append(album.get('id'))

        total_albums_ids = len(artist_albums_ids)
        print(f'Total albums: {total_albums_ids}')

        several_albums_params = {
            'ids': ''
        }

        # 6 requests above, 54 requests below left
        albums_json = list()
        tracks_json = list()
        id_offset = 20
        for i in range(0, total_albums_ids, id_offset):
            several_albums_params['ids'] = ','.join(artist_albums_ids[i:i + id_offset])
            # max 100 albums or singles = 5 requests (5 * 20)
            response = requests.get(
                'https://api.spotify.com/v1/albums',
                params=several_albums_params,
                headers=headers
            )
            time.sleep(timeout)
            request_count += 1
            print(f"[Request {request_count} - {response.status_code}]")

            album_data = response.json().get('albums')
            for album in album_data:
                print()
                print(f"Album Name: {album.get('name')}")
                album_id = album.get('id')
                print(f"Album ID: {album_id}")
                print(f"Album Type: {album.get('album_type')}")
                print(f"Album Date: {album.get('release_date')}")
                print(f"Album Genres: {album.get('genres')}")
                print(f"Album Label: {album.get('label')}")
                print(f"Album Popularity: {album.get('popularity')}")

                album_for_json = Album(
                    album.get('name'),
                    album_id,
                    album.get('album_type'),
                    album.get('release_date'),
                    album.get('genres'),
                    album.get('label'),
                    album.get('popularity')
                )

                albums_json.append(album_for_json)

                albums_tracks_json = list()
                album_tracks_ids = list()
                album_tracks = album.get('tracks').get('items')
                for track in album_tracks:
                    print()
                    print(f"Track Name: {track.get('name')}")
                    track_id = track.get('id')
                    print(f"Track ID: {track_id}")
                    album_tracks_ids.append(track_id)
                    print('Track Artists:')
                    track_artists = list()
                    for track_artist in track.get('artists'):
                        track_artists.append(track_artist.get('id'))
                    print(track_artists)
                    print(f"Track Album ID: {[album_id]}")
                    print(f"Track Duration: {track.get('duration_ms')}")
                    print(f"Track Explicit: {track.get('explicit')}")

                    track_for_json = Track(
                        track.get('name'),
                        track_id,
                        track_artists,
                        [album_id],
                        track.get('duration_ms'),
                        track.get('explicit')
                    )
                    albums_tracks_json.append(track_for_json)

                total_tracks_ids = len(album_tracks_ids)
                print(f'Total tracks: {total_tracks_ids}')

                several_tracks_params = {
                    'ids': ''
                }

                track_id_offset = 50
                for j in range(0, total_tracks_ids, track_id_offset):
                    several_tracks_params['ids'] = ','.join(album_tracks_ids[j:j + track_id_offset])
                    # max 100 tracks = 2 requests per album
                    response = requests.get(
                        'https://api.spotify.com/v1/tracks',
                        params=several_tracks_params,
                        headers=headers
                    )
                    time.sleep(timeout)
                    request_count += 1
                    print(f"[Request {request_count} - {response.status_code}]")

                    tracks_data = response.json().get('tracks')
                    for track_obj in tracks_data:
                        print(f"Track ID: {track_obj.get('id')}")
                        print(f"Track Popularity: {track_obj.get('popularity')}")

                        for tracks_i in albums_tracks_json:
                            if tracks_i.track_id == track_obj.get('id'):
                                tracks_i.popularity = track_obj.get('popularity')

                several_features_params = {
                    'ids': '',
                }

                track_features_offset = 100
                for k in range(0, total_tracks_ids, track_features_offset):
                    several_features_params['ids'] = ','.join(album_tracks_ids[k: k + track_features_offset])
                    # max 100 tracks = 1 request per album
                    response = requests.get(
                        'https://api.spotify.com/v1/audio-features',
                        params=several_features_params,
                        headers=headers
                    )
                    time.sleep(timeout)
                    request_count += 1
                    print(f"[Request {request_count} - {response.status_code}]")

                    features_data = response.json().get('audio_features')
                    for features_track in features_data:
                        print(f"Track ID: {features_track.get('id')}")
                        print(f"Track Acousticness: {features_track.get('acousticness')}")
                        print(f"Track Danceability: {features_track.get('danceability')}")
                        print(f"Track Energy: {features_track.get('energy')}")
                        print(f"Track Instrumentalness: {features_track.get('instrumentalness')}")
                        print(f"Track Key: {features_track.get('key')}")
                        print(f"Track Liveness: {features_track.get('liveness')}")
                        print(f"Track Loudness: {features_track.get('loudness')}")
                        print(f"Track Mode: {features_track.get('mode')}")
                        print(f"Track Speechiness: {features_track.get('speechiness')}")
                        print(f"Track Tempo: {features_track.get('tempo')}")
                        print(f"Track Time signature: {features_track.get('time_signature')}")
                        print(f"Track Valence: {features_track.get('valence')}")

                        for tracks_j in albums_tracks_json:
                            if tracks_j.track_id == features_track.get('id'):
                                tracks_j.acousticness = features_track.get('acousticness')
                                tracks_j.danceability = features_track.get('danceability')
                                tracks_j.energy = features_track.get('energy')
                                tracks_j.instrumentalness = features_track.get('instrumentalness')
                                tracks_j.key = features_track.get('key')
                                tracks_j.liveness = features_track.get('liveness')
                                tracks_j.loudness = features_track.get('loudness')
                                tracks_j.mode = features_track.get('mode')
                                tracks_j.speechiness = features_track.get('speechiness')
                                tracks_j.tempo = features_track.get('tempo')
                                tracks_j.time_signature = features_track.get('time_signature')
                                tracks_j.valence = features_track.get('valence')
                                # To Do: Track Playcount

                tracks_json.append(albums_tracks_json)

        artist_for_json.albums = albums_json
        artist_for_json.tracks = tracks_json

        print(artist_for_json)
        json_string = json.dumps(artist_for_json, indent=4, ensure_ascii=False, default=lambda x: x.__dict__)
        print(json_string)
        with open(f'resources/artist-{artist_id}.json', 'w', encoding='utf-8') as file:
            file.write(json_string)


if __name__ == '__main__':
    main()