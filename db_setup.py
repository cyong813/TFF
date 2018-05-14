from sqlalchemy import *
from googleplaces import GooglePlaces, types, lang
import sys
import postgres_tables

con, meta = postgres_tables.connect('postgres','root','taipei_places')

#Loads up each table to allow insertion/other queries
person = Table('person', meta, autoload_with=con)
vendor = Table('vendor', meta, autoload_with=con)
review = Table('review', meta, autoload_with=con)
category = Table('category', meta, autoload_with=con)
likes = Table('likes', meta, autoload_with=con)
has = Table('has', meta, autoload_with=con)

#for multilanguage decode
non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
google_places = GooglePlaces('AIzaSyAb5-uEqOW_3qqu0XLw8_awSBMj8QdORQA')

#user input for keyword --> category
keyw = input("Please enter desired search: ")

#Immediately insert category name (which is the keyword)
cStatement = category.insert().values(cName=keyw)
con.execute(cStatement)

# You may prefer to use the text_search API, instead.
query_result = google_places.nearby_search(
        location='Taipei, Taiwan', keyword=keyw,
        radius=20000, types=[types.TYPE_FOOD])

for place in query_result.places:
    # Returned places from a query are place summaries.
    pvID = place.place_id
    pName = place.name
    pLat = place.geo_location['lat']
    pLong = place.geo_location['lng']

    # The following method has to make a further API call.
    place.get_details()    
    # Referencing any of the attributes below, prior to making a call to
    # get_details() will raise a googleplaces.GooglePlacesAttributeError.
    #print(place.details) # A dict matching the JSON response from Google.

    pDistrict = place.details['address_components'][2]['long_name']
    pAddress = place.formatted_address
    pRating = place.rating
    
    # Getting place photos
    for photo in place.photos:
        photo.get(maxheight=500, maxwidth=500)
        pIcon = photo.url #get first photo
        break
    
    pStatement = vendor.insert().values(vID=pvID,vname=pName,address=pAddress,district=pDistrict,latitude=pLat,longitude=pLong,rating=pRating, icon=pIcon)
    con.execute(pStatement)

    #Insert into Has table
    hStatement = has.insert().values(cName=keyw,vID=pvID)
    con.execute(hStatement)
    
    #Insert reviews for Review table
    #get reviews (dict, but bc translate need to convert to string FOR NOW)
    #print(str(place.details['reviews']).translate(non_bmp_map))
    for rev in place.details['reviews']:
        rAuthor = str(rev['author_name']).translate(non_bmp_map)
        revID = str(rev['author_url']).translate(non_bmp_map)
        rDescription = str(rev['text']).translate(non_bmp_map)
        rRating = str(rev['rating']).translate(non_bmp_map)
        rStatement = review.insert().values(rID=revID,author=rAuthor,description=rDescription,rating=rRating,vID=pvID)
        con.execute(rStatement)
        
    











