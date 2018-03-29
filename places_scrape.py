from googleplaces import GooglePlaces, types, lang
import sys

#for multilanguage decode
non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
google_places = GooglePlaces('YOUR API KEY')

#user input for keyword --> category
#keyw = user_input("Please enter desired search: ")

#def gscrape(keyw):

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
    pCity = place.details['address_components'][2]['long_name']
    pAddress = place.formatted_address
    pRating = place.rating

    #Insert reviews for Review table
    #get reviews (dict, but bc translate need to convert to string FOR NOW)
    #print(str(place.details['reviews']).translate(non_bmp_map))
    for review in place.details['reviews']:
        rAuthor = str(review['author_name']).translate(non_bmp_map)
        rID = str(review['author_url']).translate(non_bmp_map)
        rDescription = str(review['text']).translate(non_bmp_map)
        rRating = str(review['rating']).translate(non_bmp_map)
        

    
