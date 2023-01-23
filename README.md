# YouTube_channels_analysis

Este projeto de extração automática foi construído em **Python 3** e fornece/modela dados da API aberta do YouTube.

Permite a análise e acompanhamento da performance de múltiplos canais do YouTube, buscando dados de views, likes, comments, subscribers, ID's e artistas.

## Requeriments:

    !pip install --upgrade google-api-python-client
    from googleapiclient.discovery import build
    import pandas as pd


### Your API Key
Para acessar os dados você precisa atribuir à variável "apiKey" a sua API Key do YouTube Data API v3 (em __ _init_ __).

    def __init__(self, gravadoras):
        api_service_name = 'youtube'
        api_version = 'v3'
        apiKey = "YOUR_API_KEY"
        self.youtube = build(api_service_name, api_version, developerKey=apiKey)

## INPUTS
Necessário atribuir no dicionário 'gravadoras' os ChannelID's dos canais que deseja visualizar.
Vide exemplo abaixo:
    
    gravadoras = {
    'Vevo Brasil': 'UCPZ-rkkRqY6OnjNBFs0LAJA',
    'Universal Music': 'UCiIkNiQDVwsvG835tAD1zuA',
    'Warner Brasil': 'UCYxLlKfySq3RVLKdNSQ1Gug',
    'Disney Music VEVO': 'UCgwv23FVv3lqh567yagXfNg
    }

Para consultar o ChannelID, acesse o canal via YouTube e clique com o botão direito em **"View Page Source"**, ou através do atalho "Ctrl + U".
Ali você pode buscar o Channel ID que estará no seguinte formato:

    <link itemprop="url" href="http://www.youtube.com/channel/#channelID">

# Code Run!
Todos os métodos definidos estão dentro da classe **Youtube**. 

### Class Youtube
A classe possui os atributos/elementos:

    def __init__(self, gravadoras):
        api_service_name = 'youtube'
        api_version = 'v3'
        apiKey = "YOUR_API_KEY"
        self.youtube = build(api_service_name, api_version, developerKey=apiKey)
        self.gravadoras = gravadoras
        self.dados_canal = []
        self.total_playlist_IDs = []
        self.videos_IDs = []
        self.videos_stats = []
        self.list_titles = []
        self.list_artists = []
        

### Run( )
        youtube = Youtube(gravadoras)
        youtube.run()
Este método executa todos os métodos declarados na Classe Youtube, registrados no arquivo _etl.py_.

São eles:

        self.get_gravadoras_statistics()
        self.get_df_videosids()
        self.get_videos_statistics()
        self.get_artists()
        self.get_dataframes()
        self.get_csv_file()

A seguir, são explicados cada um.

### get_gravadoras_statistics( )
Extrai os dados gerais do canal de cada gravadora em um dicionário e armazena em uma lista.

Armazena em outra lista a _playlistID_ de cada canal.

        request = self.youtube.channels().list(part="snippet,contentDetails,statistics", id=','.join(self.gravadoras.values()))
        response = request.execute()

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

### get_df_videosids( )
Busca o _VideoID_ de todos os vídeos das playlists extraídas e armazena em uma lista de dicionários.

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

### get_videos_statistics( )
Busca os _statistics_ e os _títulos_ de cada video a partir do VideoID, formando duas listas de dicionários.

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

### get_artists( )
Extrai os artistas de cada vídeo baseando-se no título do vídeo, que usualmente segue a regra "NOME DO ARTISTA - NOME DA MÚSICA". Armazena os resultados como dicionários em uma lista.

        for list in self.list_titles:
            title = list['Titulo']
            artist = title.split('-')[0].strip()
            data = {
                'VideoID': list['VideoID'],
                'Artist': artist
            }
            self.list_artists.append(data)

### get_dataframes( )
Usando Pandas, transforma cada lista de dicionários extraída em um **Data Frame**, que serão mesclados e formatados segundo a necessidade.

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

        self.df_geral['PublishDate'].astype('datetime64')
        self.df_geral['PublishDate'].sort_values().value_counts()

        numeric_columns = ['Subscribers', 'ChannelViews', 'ChannelTotalVideos']
        self.df_dados_canais[numeric_columns] = self.df_dados_canais[numeric_columns].apply(pd.to_numeric, errors='coerce', axis=1)

A saída deste método são duas tabelas: 
- df_geral: armazena as estatísticas de cada vídeo como likes, views e comments, relacionando com os canais, artistas, data e hora de publicação.


- df_dados_canais: armazena os dados gerais do canal, como subscribers, channel views e channel total videos.


### get_csv_file( )
Exporta os Data Frames para arquivos .CSV.

        file_name = 'Dados performance.csv'
        self.df_geral.to_csv(file_name, sep=';', encoding='mbcs')

        file_name = 'Dados gravadoras.csv'
        self.df_dados_canais.to_csv(file_name, sep=';', encoding='mbcs')


## Referências

Documentação YouTube API v3:
https://developers.google.com/youtube/v3/docs

Obtenha sua API Key do Google API Console:
https://console.cloud.google.com/apis/dashboard?project=wired-episode-374715

## Contato

Para bugs, reclamações ou sugestões, envie um e-mail para leopm98@gmail.com ;)

