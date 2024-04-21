from pytube import YouTube
import io
from ytmusicapi import YTMusic

if __name__ == '__main__':
    ytmusic = YTMusic("oauth.json")

    # # limit doesnt work
    # # radio function
    # res = ytmusic.get_watch_playlist(playlistId="PL5jlSbUnZfpKbEd3AL_3rUwGwIKWQiLeY", limit=9, radio=True)
    # print(res)
    # # keys = res.__dict__.keys()
    # for k in res:
    #     print(k, res[k])
    #
    # print("------------")
    # for d in res["tracks"]:
    #     print(d)
    # print(len(res["tracks"]))

    # res = ytmusic.get_song("ui_u0M7_hjs")
    # for k in res:
    #     print(k, res[k])

    yt = YouTube("https://music.youtube.com/watch?v=ui_u0M7_hjs")
    b = io.BytesIO()
    # download as file or buffer
    # both are same
    # video = yt.streams.filter(only_audio=True).first().download()
    video = yt.streams.filter(only_audio=True).first().stream_to_buffer(b)
    # After writing, you may want to reset the buffer's position to the beginning
    b.seek(0)
    # Read the contents of the buffer
    data = b.read()
    # write to disk
    with open("test2.mp3", 'wb') as mp3_file:
        mp3_file.write(data)



