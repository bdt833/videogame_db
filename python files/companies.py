import requests, time, psycopg2

conn = psycopg2.connect("dbname='**' user='**' host='localhost' password='**'")
cur = conn.cursor()

dict_defaults = ['developed', 'published', 'parent']

url = "https://api.igdb.com/v4/companies"

lim = 30690
offset = 0

while offset < lim:
    payload =  f"""
        fields id, name, developed, published, parent;
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

    cur.executemany("""INSERT INTO companies(company_id,name, developed, published, parent) VALUES (%(id)s, %(name)s, %(developed)s, %(published)s, %(parent)s)""", json_data)

    offset += 500
    time.sleep(0.250)

    
conn.commit()