library(RPostgreSQL)
library(rvest)
library(tidyverse)

#connect to the PostgreSQL database, then import the data
driver <- dbDriver("PostgreSQL")
con <- dbConnect(driver, dbname = "games", user = confidential$user, password = confidential$password, port = "5433")
games <- dbGetQuery(con, "select * from games where critic_rating > 80 and user_rating > 80 order by total_rating desc;")

#transform data to have + instead of space, used for URL searching
game_names <- games %>% transmute(name = str_replace_all(name, "[:blank:]", "+")) %>%
  mutate(name = str_remove_all(name, "[:punct:]")) %>% 
  as.data.frame()

#URL for searching game info
base_url <- "https://www.vgchartz.com/gamedb/games.php?name="

#create list of URLs by using the game names vector
urls <- c()
for (i in 1:nrow(game_names)) {
  urls[i] <- str_glue({base_url}, {game_names[i,1]})
}

vg_data <- function(url) {
  require(dplyr)
  require(rvest)
  y <- F #dummy variable indicating sales are missing
  vg <- read_html(url)
  
  #this xml query finds the sales data, which has 7 entries
  vg_sales <- vg %>%
    html_nodes("body") %>%
    xml2::xml_find_all("//td[contains(@align,'center')]") %>%
    html_text()
  vg_len <- length(vg_sales)
  
  #checks if vg_len = 0, meaning that sales are missing
  if (vg_len == 0) { y <- T } else {
    
    # query handling when only one result comes up
    if (vg_len <= 7) { 
      sales <- vg_sales[5]
      
      #extracts the platform that sales were on 
      platform <- vg %>%
        html_nodes("body") %>%
        xml2::xml_find_all("//td[@align]") %>%
        html_children()  %>%
        as.character()  %>%
        str_split("alt")  %>%
        unlist()  %>%
        nth(2)  %>%
        str_split("\"")  %>%
        unlist()  %>%
        nth(2)
      
      #extracts the name of the game for verification
      names <- vg %>% 
        html_nodes("body") %>% 
        xml2::xml_find_all("//td[contains(@style,'font-size:12pt;')]") %>% 
        html_text() %>%
        str_split("Read the review") %>% 
        unlist() %>% 
        nth(1) %>% 
        trimws() #removes white space padding around the name
    } else {
      
      #query handling for when multiple results come up, i.e. "God of War" returns 5+ results
      
      #find number of entries, then create empty sales/platform/names vectors
      long <- length(vg_sales)/7
      sales <- vector(mode = "character", length = long)
      platform <- vector(mode = "character", length = long)
      names <- vector(mode = "character", length = long)
      
      #same function as above for extracting the sales, platform, and name, iterating over number of entries
      for (i in 1:long) {
        sales[i] <- vg_sales[5]
        platform[i] <- vg %>%
          html_nodes("body") %>%
          xml2::xml_find_all("//td[@align]") %>%
          html_children()  %>%
          as.character() %>%
          nth(i) %>%
          str_split("alt")  %>%
          unlist()  %>%
          nth(2)  %>%
          str_split("\"")  %>%
          unlist()  %>%
          nth(2)
        names[i] <- vg %>% 
          html_nodes("body") %>% 
          xml2::xml_find_all("//td[contains(@style,'font-size:12pt;')]") %>% 
          html_text() %>% 
          nth(i) %>%
          str_split("Read the review") %>% 
          unlist() %>% 
          nth(1) %>% 
          trimws()
        
        #remove the data corresponding to the first entry
        vg_sales <- vg_sales[-1:-7]
      }
    }
  }
  #if dummy variable is True, then make entries NA
  if (y == T) {
    x <- NA
  } else {
    #create a dataframe with sales, platform, name info, filtering out irrelevant results
    x <- data.frame(sales, platform, names) %>% filter(sales != "N/A", platform != "Series")
  }
}


sales <- list()

#do a for loop over the list of URLs to store the sales data into a list
#print i to show which number the iteration is on, along with a 15 second pause
#to prevent sending too many requests to the server
for (i in 1:length(urls)) {
  sales[[i]] <- vg_data(urls[i])
  print(i)
  Sys.sleep(15)
}


#create empty dataframe to put sales data into
sales_df <- tibble(1,2,3)
colnames(sales_df) <- c("sales", "platform", "names")

#iterate over each list entry in sales to extract sales, platform, names
for (i in 1:length(sales)) {
  #find num of rows for each list entry
  rows <- nrow(sales[[i]])
  
  #some row values may be null or length 0; do nothing, else enter the actual data
  if (is.null(rows)) {
    invisible()
  } else if (rows == 0) {
    invisible()
  } else {
    for (j in 1:rows) { 
      sales_df <- rbind(sales_df, sales[[i]][j,])
    }
  }
}