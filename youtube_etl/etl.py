# -*- encoding: utf-8 -*-
import pandas as pd
import plotly.express as px
from googleapiclient.discovery import build
pd.set_option('display.max_columns', None)
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
        self.list_artists = []

    def run(self):
        self.get_gravadoras_statistics()
        self.get_df_videosids()
        self.get_videos_statistics()
        self.get_artists_and_date()
        self.get_dataframes()
        self.get_excel_file()
        print('\nRun concluido sem erros')
        
    def get_gravadoras_statistics(self):
        request = self.youtube.channels().list(part="snippet,contentDetails,statistics", id=','.join(self.gravadoras.values()))
        response = request.execute()
        print('Identificar onde está o ID:', response)
        for item in response['items']:
            data = {
                'ChannelName': item['snippet']['title'],
                'ChannelID': item['id'],
                'Subscribers': item['statistics']['subscriberCount'],
                'ChannelViews': item['statistics']['viewCount'],
                'ChannelTotalVideos': item['statistics']['videoCount'],
                'ChannelPlaylistId': item['contentDetails']['relatedPlaylists']['uploads']
            }
            self.dados_canal.append(data)
            self.total_playlist_IDs.append(data['ChannelPlaylistId'])
        print('\nIDs das playlists:', self.total_playlist_IDs)
        print('\nDados dos canais:', self.dados_canal)

    def get_df_videosids(self):
        for playlist_id in self.total_playlist_IDs:
            request = self.youtube.playlistItems().list(part='snippet,contentDetails', playlistId=playlist_id, maxResults=50)
            response = request.execute()

            for item in response['items']:
                data = {
                    'VideoID': item['contentDetails']['videoId'],
                    'ChannelID': item['snippet']['channelId'],
                    'ChannelName': item['snippet']['channelTitle']
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
                            'ChannelID': item['snippet']['channelId'],
                            'ChannelName': item['snippet']['channelTitle']
                        }
                        self.videos_IDs.append(data)
                        next_page_token = response.get('nextPageToken')
        print('\nIDs dos videos:', self.videos_IDs)

    def get_videos_statistics(self):
        for item in self.videos_IDs:
            self.video_id = item['VideoID']
            estatisticas_videos = self.youtube.videos().list(id=self.video_id, part='statistics, snippet')
            response = estatisticas_videos.execute()

            for item in response['items']:
                data = {
                    'Titulo': item['snippet']['title'],
                    'PublishDate': item['snippet']['publishedAt'],
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


    def get_artists_and_date(self):
        for list in self.list_titles:
            title = list['Titulo']
            artist = title.split('-')[0].strip()
            data = {
                'VideoID': list['VideoID'],
                'Artist': artist
            }
            self.list_artists.append(data)
        print(self.list_artists)

    def get_dataframes(self):
        self.df_dados_canais = pd.DataFrame(self.dados_canal)
        self.df_videos_ids = pd.DataFrame(self.videos_IDs)
        self.df_videos_stats = pd.DataFrame(self.videos_stats)
        self.df_titulos = pd.DataFrame(self.list_titles)
        self.df_artistas = pd.DataFrame(self.list_artists)

        self.df_videos_stats.columns = ['ViewsCount', 'LikeCount', 'FavoriteCount', 'CommentCount', 'VideoID']
        self.df_titulos[['PublishDate', 'PublishTime']] = self.df_titulos['PublishDate'].str.split('T', n=1, expand=True)

        self.df_geral = self.df_videos_ids.merge(self.df_videos_stats, how='outer').merge(self.df_titulos, how='outer').merge(self.df_artistas, how='outer')

        self.df_geral = self.df_geral[['ChannelName', 'ChannelID', 'VideoID', 'Titulo', 'Artist', 'PublishDate', 'PublishTime', 'ViewsCount', 'LikeCount',
                             'FavoriteCount', 'CommentCount']]

        numeric_columns = ['ViewsCount', 'LikeCount', 'FavoriteCount', 'CommentCount']
        self.df_geral[numeric_columns] = self.df_geral[numeric_columns].apply(pd.to_numeric, errors='coerce', axis=1)

        self.df_geral['PublishDate'].sort_values().value_counts()
        print(self.df_geral)

        numeric_columns = ['Subscribers', 'ChannelViews', 'ChannelTotalVideos']
        self.df_dados_canais[numeric_columns] = self.df_dados_canais[numeric_columns].apply(pd.to_numeric, errors='coerce', axis=1)

        print(self.df_dados_canais)
        print(self.df_dados_canais.dtypes)

    def get_excel_file(self):
        file_name = 'Dados performance.xlsx'
        self.df_geral.to_excel(file_name)

        file_name = 'Dados gravadoras.xlsx'
        self.df_dados_canais.to_excel(file_name)


# if __name__ == '__main__'