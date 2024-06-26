"""Module for additional aggregator to collect related artist data from Spotify."""
import json

import requests
from loguru import logger


def get_related_artists(artists_ids, headers, stage=0):
    """Function for finding similar artists by their artists_ids,
    query headers and number of stages are used to access the service"""
    artists_ids = list(set(artists_ids))
    total_artists = len(artists_ids)

    artists_ids_list = []
    artists_ids_list.extend(artists_ids)
    process_num = 0
    for artist_id in artists_ids:
        process_num += 1
        logger.debug(f'Collect {process_num} of {total_artists}')
        response = requests.get(
            f'https://api.spotify.com/v1/artists/{artist_id}/related-artists',
            headers=headers,
            timeout=10
        )

        for artist in response.json().get('artists'):
            artists_ids_list.append(artist.get('id'))

    logger.debug(f'==============STAGE={stage}=============')
    logger.info(f'       Total related artists: {len(artists_ids_list)}')
    logger.info(f'Total unique related artists: {len(set(artists_ids_list))}')
    logger.debug('==================================')

    artists_ids_list = list(set(artists_ids_list))

    return artists_ids_list


def artist_aggregate_main(source_file_path, id_file_path, headers):
    """Main function for data aggregation."""
    logger.info('Starting artist aggregation')
    with open(
            source_file_path,
            mode='r',
            encoding='utf-8'
    ) as file:
        artists_data = json.load(file)

    followed_artists_ids = []
    for artist in artists_data.get('artists'):
        followed_artists_ids.append(artist.get('uri').split(':')[2])

    logger.info(f"Artist aggregation stage one")
    artists_ids_list_stage_one = get_related_artists(
        followed_artists_ids,
        headers=headers,
        stage=1
    )

    logger.info(f"Artist aggregation stage two")
    artists_ids_list = get_related_artists(
        artists_ids_list_stage_one,
        headers=headers,
        stage=2
    )

    json_string = json.dumps(
        artists_ids_list,
        indent=4,
        ensure_ascii=False
    )

    with open(
            id_file_path,
            mode='w',
            encoding='utf-8'
    ) as file:
        file.write(json_string)
    logger.info(f"Artist aggregation complete")

# if __name__ == '__main__':
#     artist_aggregate_main(
#         source_file_path='src/aggregator/resources/spotify-followed-artists.json',
#         id_file_path='src/aggregator/resources/artists-ids-list.json',
#         headers={'Authorization': f'{token_type}  {access_token}'}
#     )
