import requests, time, psycopg2

conn = psycopg2.connect("dbname='**' user='**' host='localhost' password='**'")
cur = conn.cursor()

dict_defaults = ['alternative_name', 'abbreviation', 'generation', 'platform_family', 'versions']

url = "https://api.igdb.com/v4/platforms"

lim = 500
offset = 0

while offset < lim:
    payload =  f"""
        fields id, name, alternative_name, abbreviation, generation, platform_family, versions;
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
    
    cur.executemany("""INSERT INTO platforms(platform_id,name,alternative_name,abbreviation,generation,platform_family,versions) VALUES (%(id)s, %(name)s, %(alternative_name)s, %(abbreviation)s, %(generation)s, %(platform_family)s, %(versions)s)""", json_data)

    offset += 500
    time.sleep(0.250)

    
conn.commit()