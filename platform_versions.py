import requests, time, psycopg2

conn = psycopg2.connect("dbname='**' user='**' host='localhost' password='**'")
cur = conn.cursor()

dict_defaults = ['companies', 'cpu', 'graphics', 'memory', 'os', 'storage', 'sound']

url = "https://api.igdb.com/v4/platform_versions"

lim = 500
offset = 0

while offset < lim:
    payload =  f"""
        fields id, name, companies, cpu, graphics, memory, os, storage, sound;
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


    cur.executemany("""INSERT INTO platform_versions(platform_version_id,name, platform_companies, cpu, graphics, memory, os, storage, sound) VALUES (%(id)s, %(name)s, %(companies)s, %(cpu)s, %(graphics)s, %(memory)s, %(os)s, %(storage)s, %(sound)s)""", json_data)

    offset += 500
    time.sleep(0.250)

    
conn.commit()