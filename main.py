from youtube_etl.etl import Youtube

gravadoras = {
    'Vevo': 'UC2pmfLm7iq6Ov1UwYrWYkZA',
    'Universal': 'UCiIkNiQDVwsvG835tAD1zuA',
    'Warner Brasil': 'UCYxLlKfySq3RVLKdNSQ1Gug',
    'Disney Music VEVO': 'UCgwv23FVv3lqh567yagXfNg'
    }

if __name__ == '__main__':
    youtube = Youtube(gravadoras)
    youtube.run()
