import requests, time, psycopg2

conn = psycopg2.connect("dbname='**' user='**' host='localhost' password='**'")
cur = conn.cursor()

url = "https://api.igdb.com/v4/platform_version_companies"

lim = 500
offset = 0

while offset < lim:
    payload =  f"""
        fields id, company, developer, manufacturer;
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

    cur.executemany("""INSERT INTO platform_company_id(platform_company_id,company_id, developer, manufacturer) VALUES (%(id)s, %(company)s, %(developer)s, %(manufacturer)s)""", json_data)

    offset += 500
    time.sleep(0.250)

    
conn.commit()