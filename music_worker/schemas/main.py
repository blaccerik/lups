from enum import Enum
from typing import List, Dict

from pydantic import BaseModel, constr


class Artist(BaseModel):
    id: str
    name: constr(max_length=100)


class SongType(str, Enum):
    ugc = 'MUSIC_VIDEO_TYPE_UGC'
    atv = 'MUSIC_VIDEO_TYPE_ATV'
    omv = 'MUSIC_VIDEO_TYPE_OMV'
    osm = 'OFFICIAL_SOURCE_MUSIC'
    mvtpe = 'MUSIC_VIDEO_TYPE_PODCAST_EPISODE'


class Song(BaseModel):
    id: str
    title: constr(max_length=100)
    length: int
    artist: Artist | None
    type: SongType


class Result(BaseModel):
    artist_image_ids: List[str]
    songs: Dict[str, str]
