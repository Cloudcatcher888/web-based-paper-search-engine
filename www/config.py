
class Config:
    conference_list = ['iclr', 'icml', 'nips','ijcai','kdd','sigir']
    db_path = '/Users/wangzhikai/vscodeProjs/web/www/ludweb.db'
    sim_alg = 'tfidf' 
    #bert: 原生支持增量更新，效果不太正常
    #tfidf 原生不支持增量更新，效果稳定正常