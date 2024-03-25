import json

import pytest

from src.aggregator.artist_aggregate import get_related_artists, artist_aggregate_main
from src.aggregator.auth_credentials import access_token, token_type, client_headers
from src.aggregator.classes.album import Album
from src.aggregator.classes.artist import Artist
from src.aggregator.classes.track import Track
from src.aggregator.stats_utils import get_artist_response_template

params_for_get_related = (
    (
        ['00FQb4jTyendYWaN8pK0wa'],
        [{"artists": [{"id": "1"}, {"id": "2"}]}]
    ),
    (
        ['$2_.&+=-~()\\qS4*?!@#%^'],
        [{"artists": []}]
    ),
    (
        [''],
        [{"artists": []}]
    ),
    (
        [
            '00FQb4jTyendYWaN8pK0wa',
            '0M2HHtY3OOQzIZxrHkbJLT'
        ],
        [
            {"artists": [{"id": "1"}, {"id": "2"}]},
            {"artists": [{"id": "3"}, {"id": "4"}]},
        ]
    ),
)

get_related_ids = [
    (
        f'test_id: {par[0]}, '
        f'json_data-{params_for_get_related.index(par)}'
    ) for par in params_for_get_related
]


@pytest.mark.unit
@pytest.mark.parametrize(
    'test_ids, json_datas',
    params_for_get_related,
    ids=get_related_ids
)
def test_get_related_artists(requests_mock, test_ids, json_datas):
    """Test get_related_artists function with parameters test_ids as artists_ids
     with options of one positive id, negative id, empty id and two id."""
    for test_id in test_ids:
        requests_mock.get(
            url=f'https://api.spotify.com/v1/artists/{test_id}/related-artists',
            json=json_datas[test_ids.index(test_id)]
        )

    actual_ids_list = sorted(
        get_related_artists(
            test_ids,
            headers={}
        )
    )

    json_ids = [
        art_id.get('id') for json_data in json_datas
        for val in json_data.values() for art_id in val
    ]
    json_ids.extend(test_ids)

    expected_ids_list = sorted(json_ids)

    assert actual_ids_list == expected_ids_list


def mock_get_related_return(*args, **kwargs):
    """Mock function for the correct return values
     for the artist_aggregate_main test."""
    # prepare test data for test case 1
    with open(
            'tests/resources/followed-artists-test-0.json',
            mode='r',
            encoding='utf-8'
    ) as file:
        followed_test_one = json.load(file)

    followed_ids_one = []
    for artist in followed_test_one.get('artists'):
        followed_ids_one.append(artist.get('uri').split(':')[2])

    with open(
            'tests/resources/stage_one_ids-0.json',
            mode='r',
            encoding='utf-8'
    ) as stage_one_file:
        test_one_stage_one = json.load(stage_one_file)

    test_one_stage_one_ids = [artist for artist in test_one_stage_one]

    with open(
            'tests/resources/stage_two_ids-0.json',
            mode='r',
            encoding='utf-8'
    ) as stage_two_file:
        test_one_stage_two = json.load(stage_two_file)

    test_one_stage_two_ids = [artist for artist in test_one_stage_two]

    # prepare test data for test case 2
    with open(
            'tests/resources/followed-artists-test-1.json',
            mode='r',
            encoding='utf-8'
    ) as file:
        followed_test_two = json.load(file)

    followed_ids_two = []
    for artist in followed_test_two.get('artists'):
        followed_ids_two.append(artist.get('uri').split(':')[2])

    with open(
            'tests/resources/stage_one_ids-1.json',
            mode='r',
            encoding='utf-8'
    ) as stage_one_file:
        test_two_stage_one = json.load(stage_one_file)

    test_two_stage_one_ids = [artist for artist in test_two_stage_one]

    with open(
            'tests/resources/stage_two_ids-1.json',
            mode='r',
            encoding='utf-8'
    ) as stage_two_file:
        test_two_stage_two = json.load(stage_two_file)

    test_two_stage_two_ids = [artist for artist in test_two_stage_two]

    # mock function call args templates
    if args == (followed_ids_one,) and kwargs == {
        "headers": {
            'Authorization': f'{token_type}  {access_token}',
        },
        "stage": 1
    }:
        return test_one_stage_one_ids
    elif args == (test_one_stage_one_ids,) and kwargs == {
        "headers": {
            'Authorization': f'{token_type}  {access_token}',
        },
        "stage": 2
    }:
        return test_one_stage_two_ids
    elif args == (followed_ids_two,) and kwargs == {
        "headers": {
            'Authorization': f'{token_type}  {access_token}',
        },
        "stage": 1
    }:
        return test_two_stage_one_ids
    elif args == (test_two_stage_one_ids,) and kwargs == {
        "headers": {
            'Authorization': f'{token_type}  {access_token}',
        },
        "stage": 2
    }:
        return test_two_stage_two_ids
    elif args == ([],) and kwargs == {
        "headers": {
            'Authorization': f'{token_type}  {access_token}',
        },
        "stage": 1
    }:
        return []
    elif args == ([],) and kwargs == {
        "headers": {
            'Authorization': f'{token_type}  {access_token}',
        },
        "stage": 2
    }:
        return []


params_for_artist_aggregate = (
    (
        'tests/resources/followed-artists-test-0.json',
        'tests/resources/actual-artists-ids.json',
        'tests/resources/expected-artists-ids-0.json'
    ),
    (
        'tests/resources/followed-artists-test-1.json',
        'tests/resources/actual-artists-ids.json',
        'tests/resources/expected-artists-ids-1.json'
    ),
    (
        'tests/resources/followed-artists-test-2.json',
        'tests/resources/actual-artists-ids.json',
        'tests/resources/expected-artists-ids-2.json'
    )
)

artist_aggregate_main_ids = [
    (
        f'followed-artists-test-{params_for_artist_aggregate.index(par)}.json, '
        f'actual-artists-ids.json, '
        f'expected-artists-ids-{params_for_artist_aggregate.index(par)}.json'
    ) for par in params_for_artist_aggregate
]


@pytest.mark.unit
@pytest.mark.parametrize(
    'source_file_path, id_file_path, expected_file_path',
    params_for_artist_aggregate,
    ids=artist_aggregate_main_ids
)
def test_artist_aggregate_main(
        mocker, source_file_path, id_file_path, expected_file_path):
    """Test execution of artist_aggregate_main function
     to collect related artists from source_file_path file
    with two id, one id and empty id."""
    mocker.patch(
        'src.aggregator.artist_aggregate.get_related_artists',
        new=mock_get_related_return
    )
    artist_aggregate_main(
        source_file_path=source_file_path,
        id_file_path=id_file_path
    )

    with open(
            expected_file_path,
            mode='r',
            encoding='utf-8'
    ) as file:
        expected_ids_data = json.load(file)

    with open(
            id_file_path,
            mode='r',
            encoding='utf-8'
    ) as file:
        actual_ids_data = json.load(file)

    assert sorted(expected_ids_data) == sorted(actual_ids_data)


@pytest.mark.unit
def test_artist_aggregate_main_raises_exception():
    """Test of exception call by artist_aggregate_main function
     when collecting related artists from invalid source_file_path file."""
    with pytest.raises(json.decoder.JSONDecodeError) as excinfo:
        artist_aggregate_main(
            source_file_path='tests/resources/followed-artists-test-3.json',
            id_file_path='actual-artists-ids.json'
        )
    exception_msg = excinfo.value.args[0]
    assert exception_msg == 'Expecting value: line 1 column 1 (char 0)'


params_for_album_class = (
    ("Come! See!!", "4UYc1NrDWoMpPV68It9Obh", "album", "2022-05-18", [], "M.O.O.N. Holdings", 24),
    ("", "", "", "", [], "", 0)
)

album_class_ids = [
    f'test-{params_for_album_class.index(par)}'
    for par in params_for_album_class
]


@pytest.mark.unit
@pytest.mark.parametrize(
    'album_name, album_id, album_type, release_date, genres, label, popularity',
    params_for_album_class,
    ids=album_class_ids
)
def test_album_class_methods(
        album_name, album_id, album_type, release_date, genres, label, popularity):
    """Test the Album class methods __init__, __str__, and get_album_name
     with positive and empty names."""
    test_album = Album(
        album_name=album_name,
        album_id=album_id,
        album_type=album_type,
        release_date=release_date,
        genres=genres,
        label=label,
        popularity=popularity
    )

    assert test_album.get_album_name() == album_name
    assert test_album.__str__() == f'{album_name} {album_id} {album_type}' \
                                   f' {release_date} {genres} {label} {popularity}'


@pytest.mark.unit
def test_album_class_exception():
    """Test the Album class method __init__ with negative names
     and check raising type exception."""
    with pytest.raises(TypeError) as excinfo:
        test_album = Album(
            album_name=32987,
            album_id="",
            album_type="albums",
            release_date="2022",
            genres=[],
            label="",
            popularity=0
        )
    exception_msg = excinfo.value.args[0]
    assert exception_msg == 'Album name must be string.'


params_for_artist_class = (
    (
        "0M2HHtY3OOQzIZxrHkbJLT", "M|O|O|N", 44, 129917, ["synthwave"],
        [
            {
                "album_name": "Come! See!!",
                "album_id": "4UYc1NrDWoMpPV68It9Obh",
                "album_type": "album",
                "release_date": "2022-05-18",
                "genres": [],
                "label": "M.O.O.N. Holdings",
                "popularity": 24
            }
        ],
        [
            {
                "track_name": "Kintsugi",
                "track_id": "5OILFfuKykbUDiFKJRXP5w"
            }
        ]
    ),
    ("", "", 0, 0, [], [], [])
)

artist_class_ids = [
    f'test-{params_for_artist_class.index(params)}, '
    f'name-{params[1]}'
    for params in params_for_artist_class
]


@pytest.mark.unit
@pytest.mark.parametrize(
    'artist_id, name, popularity, followers, genres, albums, tracks',
    params_for_artist_class,
    ids=artist_class_ids
)
def test_artist_class_methods(
        artist_id, name, popularity, followers, genres, albums, tracks):
    """Test the Artist class methods __init__, __str__, and get_artist_name
     with positive and empty names."""
    test_artist = Artist(
        artist_id=artist_id,
        name=name,
        popularity=popularity,
        followers=followers,
        genres=genres,
        albums=albums,
        tracks=tracks
    )

    assert test_artist.get_artist_name() == name
    assert test_artist.__str__() == f'{artist_id} {name} {popularity}' \
                                    f' {followers} {genres} {albums} {tracks}'


@pytest.mark.unit
def test_artist_class_exception():
    """Test the Artist class method __init__ with negative names
     and check raising type exception."""
    with pytest.raises(TypeError) as excinfo:
        test_artist = Artist(
            artist_id="12345",
            name=87326,
            popularity=0,
            followers=0,
            genres=[],
            albums=[],
            tracks=[]
        )
    exception_msg = excinfo.value.args[0]
    assert exception_msg == 'Artist name must be string.'


params_for_track_class = (
    (
        "Kintsugi", "5OILFfuKykbUDiFKJRXP5w",
        ["0M2HHtY3OOQzIZxrHkbJLT"], ["4UYc1NrDWoMpPV68It9Obh"],
        246323, "false", 20, 0.00949
    ),
    ("", "", [], [], 0, "", 0, 0.0)
)

track_class_ids = [
    f'test-{params_for_track_class.index(params)}, '
    f'track_name-{params[0]}'
    for params in params_for_track_class
]


@pytest.mark.unit
@pytest.mark.parametrize(
    'track_name, track_id, artists, albums, duration_ms, explicit, popularity, acousticness',
    params_for_track_class,
    ids=track_class_ids
)
def test_track_class_methods(
        track_name, track_id, artists, albums, duration_ms, explicit,
        popularity, acousticness):
    """Test the Track class methods __init__, __str__, and get_artist_name
     with positive and empty names."""
    test_track = Track(
        track_name=track_name,
        track_id=track_id,
        artists=artists,
        albums=albums,
        duration_ms=duration_ms,
        explicit=explicit,
        popularity=popularity,
        acousticness=acousticness
    )

    assert test_track.get_track_name() == track_name
    assert test_track.__str__() == f'{track_name} {track_id} {artists} {albums}' \
                                   f' {duration_ms} {explicit} {popularity}' \
                                   f' {acousticness}' + ' None' * 11


@pytest.mark.unit
def test_track_class_exception():
    """Test the Track class method __init__ with negative names
     and check raising type exception."""
    with pytest.raises(TypeError) as excinfo:
        test_track = Track(
            track_name=12345,
            track_id="",
            artists=[],
            albums=[],
            duration_ms=0,
            explicit="",
            popularity=0,
            acousticness=0.0
        )
    exception_msg = excinfo.value.args[0]
    assert exception_msg == 'Track name must be string.'


params_for_get_template = (
    ("0M2HHtY3OOQzIZxrHkbJLT", 0), ("$2_.&+=-~()\\qS4*?!@#%^", 1),
    ("", 0), ("", 1)
)


@pytest.mark.unit
@pytest.mark.parametrize(
    'artist_id, request_count', params_for_get_template)
def test_get_artist_template(
        requests_mock, get_artist_json_data, artist_id, request_count):
    """Test get_artist_response_template function with parameters artist_id
     and request_count with options of one positive id, negative id,
     empty id and empty id increased count."""
    requests_mock.get(
        url='https://api-partner.spotify.com/pathfinder/v1/query',
        headers=client_headers,
        json=get_artist_json_data
    )

    count_before = request_count
    response, request_count = get_artist_response_template(
        artist_id=artist_id,
        timeout=0,
        request_count=request_count
    )

    assert response.json() == get_artist_json_data
    assert request_count == count_before + 1
