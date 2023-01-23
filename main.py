# -*- encoding: utf-8 -*-
from youtube_etl.etl import Youtube


gravadoras = {
    'Vevo Brasil': 'UCPZ-rkkRqY6OnjNBFs0LAJA',
    'Universal Music': 'UCiIkNiQDVwsvG835tAD1zuA',
    'Warner Brasil': 'UCYxLlKfySq3RVLKdNSQ1Gug',
    'Disney Music VEVO': 'UCgwv23FVv3lqh567yagXfNg'
    }


if __name__ == '__main__':
    youtube = Youtube(gravadoras)
    youtube.run()

