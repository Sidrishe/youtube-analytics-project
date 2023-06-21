import os
import isodate
import datetime
from googleapiclient.discovery import build
from src.video import Video


class PlayList:
    """Класс для ютуб-плейлиста"""

    # YT_API_KEY скопирован из гугла и вставлен в переменные окружения
    api_key: str = os.getenv('YT_API_KEY')

    # создать специальный объект для работы с API
    youtube = build('youtube', 'v3', developerKey=api_key)

    def __init__(self, playlist_id: str) -> None:
        """Экземпляр инициализируется id плейлиста. Дальше все данные будут подтягиваться по API."""
        self.playlist_id = playlist_id
        self.playlist_info = self.youtube.playlists().list(id=self.playlist_id, part='snippet').execute()
        self.title = self.playlist_info['items'][0]['snippet']['title']
        self.url = f'https://www.youtube.com/playlist?list={self.playlist_id}'
        playlist_videos = self.youtube.playlistItems().list(playlistId=playlist_id, part='contentDetails',
                                                            maxResults=50).execute()
        self.video_ids: list[str] = [video['contentDetails']['videoId'] for video in playlist_videos['items']]

    @property
    def total_duration(self):
        video_response = self.youtube.videos().list(part='contentDetails, statistics',
                                                    id=','.join(self.video_ids)).execute()
        common_duration = datetime.timedelta()
        for video in video_response['items']:
            iso_8601_duration = video['contentDetails']['duration']
            duration = isodate.parse_duration(iso_8601_duration)
            common_duration += duration
        return common_duration

    def show_best_video(self):
        b_video = 0
        url_b_video = ''

        for id_video in self.video_ids:
            video = Video(id_video)
            if int(video.like_count) >= b_video:
                b_video = int(video.like_count)
                url_b_video = video.url
        return url_b_video
