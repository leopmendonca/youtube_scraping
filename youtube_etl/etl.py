from googleapiclient.discovery import build
# import requirements ????

class Youtube:
    def __init__(self, gravadoras):
        api_service_name = 'youtube'
        api_version = 'v3'
        apiKey = "AIzaSyA11UMy-tpt_FXxjzBFkfYk2TwLKt0C-n0"
        self.youtube = build(api_service_name, api_version, developerKey=apiKey)
        self.gravadoras = gravadoras
        self.dados_canal = []
        self.total_playlist_IDs = []
        self.videos_IDs = []
        self.videos_stats = []
        self.list_titles = []

    def run(self):
        self.get_gravadoras_statistics()
        self.get_df_videosids()
        self.get_videos_statistics()
        print('\nRun concluido sem erros')
        
    def get_gravadoras_statistics(self):
        request = self.youtube.channels().list(part="snippet,contentDetails,statistics", id=','.join(self.gravadoras.values()))
        response = request.execute()
        print('Identificar onde está o ID:', response)
        for item in response['items']:
            data = {
                'ChannelName': item['snippet']['title'],
                'ChannelID:': item['id'],
                'Subscribers': item['statistics']['subscriberCount'],
                'Views': item['statistics']['viewCount'],
                'TotalVideos': item['statistics']['videoCount'],
                'PlaylistId': item['contentDetails']['relatedPlaylists']['uploads']
            }
            self.dados_canal.append(data)
            self.total_playlist_IDs.append(data['PlaylistId'])
        print('\nIDs das playlists:', self.total_playlist_IDs)
        print('\nDados dos canais:', self.dados_canal)

    def get_df_videosids(self):
        for playlist_id in self.total_playlist_IDs:
            request = self.youtube.playlistItems().list(part='snippet,contentDetails', playlistId=playlist_id, maxResults=50)
            response = request.execute()

            for item in response['items']:
                data = {
                    'VideoID': item['contentDetails']['videoId'],
                    'ChannelID': item['snippet']['channelId']
                }
                self.videos_IDs.append(data)
            next_page_token = response.get('nextPageToken')
            more_pages = True

            while more_pages:
                if next_page_token is None:
                    more_pages = False
                else:
                    request = self.youtube.playlistItems().list(part='snippet,contentDetails', playlistId=playlist_id, maxResults=50, pageToken=next_page_token)
                    response = request.execute()

                    for item in response['items']:
                        data = {
                            'VideoID': item['contentDetails']['videoId'],
                            'ChannelID': item['snippet']['channelId']
                        }
                        self.videos_IDs.append(data)
                        next_page_token = response.get('nextPageToken')
            #PEGOU APENAS 5 VIDEOS DE CADA PLAYLIST_ID (PADRAO). PRECISA PEGAR TODOS.
            #PEGOU CHANNEL ID PARA RELACIONAR MAIS TARDE COM JOIN.
        print('\nIDs dos videos:', self.videos_IDs)

    def get_videos_statistics(self):
        for item in self.videos_IDs:
            self.video_id = item['VideoID']
            estatisticas_videos = self.youtube.videos().list(id=self.video_id, part='statistics, snippet')
            response = estatisticas_videos.execute()

            for item in response['items']:
                data = {
                    'Titulo': item['snippet']['title'],
                    'VideoID': item['id'],
                    'ChannelID': item['snippet']['channelId']
                }
                self.list_titles.append(data)
                statistics = item['statistics']
                statistics['videoid'] = item['id']
                self.videos_stats.append(statistics)
        print('\nStats de um video:', statistics)
        print('\nStats de todos os videos:', self.videos_stats)
        print('\nGeral videos:', response)
        print('\nLista titulos:', self.list_titles)


    #def dataframes(self):

# if __name__ == '__main__'