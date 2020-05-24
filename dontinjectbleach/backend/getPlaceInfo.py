from googleplaces import GooglePlaces, types, lang 
import requests 
import json 
  
API_KEY = 'AIzaSyC18UwOlFVtRkQzzC0eHOun3pAH-fizYzY'
  
google_places = GooglePlaces(API_KEY) 

query_result = google_places.nearby_search( 

        lat_lng ={'lat': 28.4089, 'lng': 77.3178}, 
        radius = 5000, 

        types =[types.TYPE_HOSPITAL]) 

if query_result.has_attributions: 
    print (query_result.html_attributions) 
  
  
for place in query_result.places: 
 
    print (place.name) 
    print("Latitude", place.geo_location['lat']) 
    print("Longitude", place.geo_location['lng']) 
    print() 