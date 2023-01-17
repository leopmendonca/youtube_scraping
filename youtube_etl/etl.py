from googleapiclient.discovery import build

class Youtube:
    def __init__(self, gravadoras):
        api_service_name = 'youtube'
        api_version = 'v3'
        apiKey = "xxxxxxxxxxxxxxxxxxxx"
        self.youtube = build(api_service_name, api_version, developerKey=apiKey)
        self.gravadoras = gravadoras
        self.tabela_dados = []
        self.total_playlist_IDs = []
        self.videos_IDs = []
        self.videos_stats = []

    def run(self):
        self.get_gravadoras_statistics()
        self.get_videosids()
        self.get_videos_statistics()
        print(1)
    def get_gravadoras_statistics(self):
        request = self.youtube.channels().list(part="snippet,contentDetails,statistics", id=','.join(self.gravadoras.values()))
        response = request.execute()

        for item in response['items']:
            data = {
                'ChannelName': item['snippet']['title'],
                'Subscribers': item['statistics']['subscriberCount'],
                'Views': item['statistics']['viewCount'],
                'TotalVideos': item['statistics']['videoCount'],
                'PlaylistId': item['contentDetails']['relatedPlaylists']['uploads']
            }
            self.tabela_dados.append(data)
            self.total_playlist_IDs.append(data['PlaylistId'])

    def get_videosids(self):
        for playlist_id in self.total_playlist_IDs:
            request = self.youtube.playlistItems().list(part='snippet,contentDetails', playlistId=playlist_id)
            response = request.execute()

            for item in response['items']:
                video_id = item['contentDetails']['videoId']
                self.videos_IDs.append(video_id)

    def get_videos_statistics(self):
        request = self.youtube.videos().list(id=','.join(self.videos_IDs), part='statistics')
        response = request.execute()
        print(response)

        for item in response['items']:
            statistics = item['statistics']
            statistics['videoid'] = item['id']
            self.videos_stats.append(statistics)

    def dataframes(self):
