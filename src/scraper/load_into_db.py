import os
import json
import requests
from datetime import datetime

for artist in sorted(os.listdir('artist_stats')):

    with open('artist_stats/' + artist) as f:
        data_raw = json.load(f)['data']['artistUnion']

    with open('artists/artist-' + artist) as f:
        model = json.load(f)

    model['followers'] = data_raw['stats']['followers']
    model['monthly_listeners'] = data_raw['stats']['monthlyListeners']
    model['world_rank'] = data_raw['stats']['worldRank']
    model['top_cities'] = data_raw['stats']['topCities']['items']

    tracks_raw = {}

    found_albums = []

    for album in model['albums']:
        found_albums.append(album['album_id'])
        with open('albums/' + album['album_id'] + '.json') as f:
            album_raw = json.load(f)['data']['albumUnion']

        for track in album_raw['tracks']['items']:
            track_id = track['track']['uri'].split(':')[-1]
            if track_id not in tracks_raw:
                tracks_raw[track_id] = []
            tracks_raw[track_id].append(track['track'])

        if 'date' in album_raw and album_raw['date'] != None and 'isoString' in album_raw['date']:
            album['release_date'] = album_raw['date']['isoString']
        elif len(album['release_date']) == 4:
            album['release_date'] = datetime.strptime(album['release_date'], '%Y').isoformat()
        else:
            print(album['release_date'])
            raise Exception

    for track in model['tracks']:
        if track['track_id'] not in tracks_raw:
            print(track['track_id'])
        else:
            track_raw = tracks_raw[track['track_id']][0]
            track['plays'] = track_raw['playcount']

    r = requests.post('http://192.168.191.64:5000/saveArtist',
            headers = {'Content-Type': 'application/json'},
            data = json.dumps(model))

    print(artist, r.status_code)
