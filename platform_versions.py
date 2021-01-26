import requests, time, psycopg2

conn = psycopg2.connect("dbname='**' user='**' host='localhost' password='**'")
cur = conn.cursor()

url = "https://api.igdb.com/v4/platform_versions"

lim = 50
offset = 0

while offset < lim:
    payload =  f"""
        fields id, name;
        \r\nlimit 50;\r\noffset {offset};
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
    
    cur.executemany("""INSERT INTO platform_family(platform_family_id,name) VALUES (%(id)s, %(name)s)""", json_data)

    offset += 50
    time.sleep(0.250)

    
conn.commit()