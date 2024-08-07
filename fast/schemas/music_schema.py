from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, constr


class Artist(BaseModel):
    id: constr(min_length=24, max_length=24)
    name: constr(max_length=100)


class SongType(str, Enum):
    ugc = 'MUSIC_VIDEO_TYPE_UGC'
    atv = 'MUSIC_VIDEO_TYPE_ATV'
    omv = 'MUSIC_VIDEO_TYPE_OMV'
    osm = 'OFFICIAL_SOURCE_MUSIC'
    mvtpe = 'MUSIC_VIDEO_TYPE_PODCAST_EPISODE'


class StatusType(str, Enum):
    ready = "ready"
    working = "working",


class Song(BaseModel):
    id: constr(min_length=11, max_length=11)
    title: constr(max_length=100)
    length: int  # in seconds
    artist: Artist | None
    type: SongType


class SongReaction(BaseModel):
    duration: int
    liked: bool


class FilterConfig(BaseModel):
    include: bool  # keep or remove certain word
    target_title: bool  # title or artist
    word: str


class Filter(BaseModel):
    id: int
    name: constr(min_length=1, max_length=100)
    config: List[FilterConfig]
    delete: Optional[bool] = None


class QueuePrevious(BaseModel):
    song: Song
    hidden: bool
