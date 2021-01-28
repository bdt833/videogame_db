import requests, time, psycopg2

conn = psycopg2.connect("dbname='**' user='**' host='localhost' password='**'")
cur = conn.cursor()

dict_defaults = ['developer', 'publisher', 'porting', 'supporting']

url = "https://api.igdb.com/v4/involved_companies"

lim = 92044
offset = 0

while offset < lim:
    payload =  f"""
        fields id, company, game, developer, publisher, porting, supporting;
        \r\nlimit 500;\r\noffset {offset};
        \r\nsort id; 
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

    cur.executemany("""INSERT INTO game_company_id(game_company_id,company_id, game_id, developer, publisher, porting, supporting) VALUES (%(id)s, %(company)s, %(game)s, %(developer)s, %(publisher)s, %(porting)s, %(supporting)s)""", json_data)

    offset += 500
    time.sleep(0.250)

    
conn.commit()