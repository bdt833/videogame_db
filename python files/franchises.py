import requests, time, psycopg2

conn = psycopg2.connect("dbname='**' user='**' host='localhost' password='**'")
cur = conn.cursor()

url = "https://api.igdb.com/v4/franchises"

lim = 2109
offset = 0

while offset < lim:
    payload =  f"""
        fields id, name, games;
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
        data.setdefault('games', None)
     
    cur.executemany("""INSERT INTO franchises(franchise_id,name,games) VALUES (%(id)s, %(name)s, %(games)s)""", json_data)

    offset += 500
    time.sleep(0.250)

    
conn.commit()