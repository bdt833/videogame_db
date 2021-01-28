import requests, time, psycopg2, datetime

#creating connection to PostgreSQL server, sensitive info censored
conn = psycopg2.connect("dbname='**' user='**' host='localhost' password='**'")
cur = conn.cursor()

#create a list of default dictionary keys, to be used later in the script for assigning default values if key is missing
dict_defaults = ['num_critic', 'total_rating_count', 'rating_count', 'platforms', 'total_rating',
                  'aggregated_rating', 'rating', 'franchise', 'genres', 'first_release_date']

#URL for POST request
url = "https://api.igdb.com/v4/games"

#limit for number of games in the database, and set initial offset
lim = 136197
offset = 0

#while loop for iterating through all of the data, 500 pieces of data at a time
while offset < lim:

    #the actual data being sent through the POST request
    payload =  f"""
        fields id, name, franchise, genres, platforms, 
        first_release_date, aggregated_rating, rating, total_rating, 
        rating_count, total_rating_count;
        \r\nlimit 500;\r\noffset {offset};
        \r\nsort id;
        """

    #header created with sensitive info censored
    headers = {
    'Client-ID': '**',
    'Authorization': 'Bearer **',
    'Content-Type': 'application/javascript',
    'Cookie': '**'
    }

    #create the POST request
    response = requests.request("POST", url, headers=headers, data = payload)

    #save the response in a list of JSON
    json_data = response.json()
    
    #iterate through each JSON object in the list
    for data in json_data:

        #setting the default key-value pairs for missing keys in the dict
        for defaults in dict_defaults:
            data.setdefault(defaults, None)

        #attempt to feature engineer num_critic based off of other values; if error due to missing values, pass
        try:
            data['num_critic'] = data['total_rating_count'] - data['rating_count']
        except:
            pass

        #attempt to change timestamp info into UTC time for entry into database, else pass if missing
        try:
            data['first_release_date'] = datetime.datetime.utcfromtimestamp(data['first_release_date']).strftime('%Y-%m-%d')
        except:
            pass
     
    #executemany inserts values into the database and iterates over the list to generate values for each list entry
    cur.executemany("""INSERT INTO games(game_id,name,franchise,genres,platforms,release_date,critic_rating,user_rating,total_rating,num_critic,num_user,num_total) VALUES (%(id)s, %(name)s, %(franchise)s, %(genres)s, %(platforms)s, %(first_release_date)s, %(aggregated_rating)s, %(rating)s, %(total_rating)s, %(num_critic)s, %(rating_count)s, %(total_rating_count)s)""", json_data)

    #increase offset value for next POST request, and pause for 0.25s since the API calls are limited to 4 per second
    offset += 500
    time.sleep(0.250)

#commit the insert to the database
conn.commit()