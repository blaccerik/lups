import json

from pytube import YouTube
import io
from ytmusicapi import YTMusic

if __name__ == '__main__':
    ytmusic = YTMusic("oauth.json")
    #
    # # # limit doesnt work
    # # # radio function
    # res = ytmusic.get_watch_playlist(
    #     videoId="5dqummhs3S8",
    #     radio=True
    # )

    file_path = "res.json"
    # with open(file_path, "w") as json_file:
    #     json.dump(res, json_file)

    with open(file_path, "r") as json_file:
        res = json.load(json_file)
    print("-----")
    for k in res:
        print(k, res[k])
    print("-----")
    tracks = res["tracks"]
    for t in tracks:
        print(t)
        for k in t:
            print(k, t[k])
        break
    print("-----")
    print(len(tracks))
    print("-----")

    res = ytmusic.get_watch_playlist(
        videoId="jqkPqfOFmbY",
        radio=True
    )
    for k in res:
        print(k, res[k])

    tracks = res["tracks"]
    for t in tracks:
        print(t)
        for k in t:
            print(k, t[k])
        break

    # print("-----")
    # res = ytmusic.get_watch_playlist(playlistId="RDAMVM5dqummhs3S8")
    # for k in res:
    #     print(k, res[k])

    # related MPTRt_hAsFhuIwCj1-1
    # gets all info about related tab
    # res = ytmusic.get_song_related("MPTRt_hAsFhuIwCj1-1")
    # for k in res:
    #     print(k)

    # res = ytmusic.get_song("ui_u0M7_hjs")
    # for k in res:
    #     print(k, res[k])

    # yt = YouTube("https://music.youtube.com/watch?v=ui_u0M7_hjs")
    # b = io.BytesIO()
    # # download as file or buffer
    # # both are same
    # # video = yt.streams.filter(only_audio=True).first().download()
    # video = yt.streams.filter(only_audio=True).first().stream_to_buffer(b)
    # # After writing, you may want to reset the buffer's position to the beginning
    # b.seek(0)
    # # Read the contents of the buffer
    # data = b.read()
    # # write to disk
    # with open("test2.mp3", 'wb') as mp3_file:
    #     mp3_file.write(data)



