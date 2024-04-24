from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, constr, Field


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
    has_audio: bool


class FilterConfig(BaseModel):
    include: bool  # keep or remove certain word
    target_title: bool  # title or artist
    word: str


class Filter(BaseModel):
    id: int
    name: constr(min_length=1, max_length=100)
    config: List[FilterConfig]
    delete: Optional[bool] = None
