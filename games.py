import requests, time, psycopg2, datetime

conn = psycopg2.connect("dbname='**' user='**' host='localhost' password='**'")
cur = conn.cursor()

dict_defaults = ['num_critic', 'total_rating_count', 'rating_count', 'platforms', 'total_rating',
                  'aggregated_rating', 'rating', 'franchise', 'genres', 'first_release_date']

url = "https://api.igdb.com/v4/games"

lim = 136197
offset = 0

while offset < lim:
    payload =  f"""
        fields id, name, franchise, genres, platforms, 
        first_release_date, aggregated_rating, rating, total_rating, 
        rating_count, total_rating_count;
        \r\nlimit 500;\r\noffset {offset};
        \r\nsort id desc;
        """
    headers = {
    'Client-ID': '**',
    'Authorization': 'Bearer **',
    'Content-Type': 'application/javascript',
    'Cookie': '**'
    }

    response = requests.request("POST", url, headers=headers, data = payload)

    json_data = response.json()
    for data in json_data:
        for defaults in dict_defaults:
            data.setdefault(defaults, None)
        try:
            data['num_critic'] = data['total_rating_count'] - data['rating_count']
        except:
            pass
        try:
            data['first_release_date'] = datetime.datetime.utcfromtimestamp(data['first_release_date']).strftime('%Y-%m-%d')
        except:
            pass
     
    cur.executemany("""INSERT INTO games(game_id,name,franchise,genres,platforms,release_date,critic_rating,user_rating,total_rating,num_critic,num_user,num_total) VALUES (%(id)s, %(name)s, %(franchise)s, %(genres)s, %(platforms)s, %(first_release_date)s, %(aggregated_rating)s, %(rating)s, %(total_rating)s, %(num_critic)s, %(rating_count)s, %(total_rating_count)s)""", json_data)

    offset += 500
    time.sleep(0.250)

conn.commit()