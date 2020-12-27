# Libraries
import requests
import json
import time
import urllib.parse

# Webex Access Token and Mapquest Key
# Choice to input Webex Access Token
choice = input("Use hard coded Webex Access Token? (y/n)")

if choice == "n" or choice == "N":
    accessToken = input("Token: ")
    accessToken = "Bearer " + accessToken
else:
    accessToken = "Bearer <Enter hard coded Webex Access Token here>"
    
# Choice to input MapQuest API Key
choice = input("Use hard coded MapQuest API Key? (y/n)")
if choice == "n" or choice == "N":
    key = input("Key: ")
else:
    key = "<Enter MapQuest API Key here>"

# Pick a Webex Teams Room in wich to check for instructions
# HTTP GET Request for webex teams rooms
r = requests.get(   "https://api.ciscospark.com/v1/rooms",
                    headers = {"Authorization": accessToken}
                )
# Check if the response from the API call was OK (r. code 200)
if not r.status_code == 200:
    raise Exception("Incorrect reply from Webex Teams API. Status code: {}. Text: {}".format(r.status_code, r.text))
# Display a list of rooms
print("List of rooms:")
rooms = r.json()["items"]
for room in rooms:
    print (room["title"])
# Searches for Name of the room and displays the room
while True:
    # Input the name of the room to be searched 
    roomNameToSearch = input("Which room should be monitored for /gps messages? ")

    # Defines a variable that will hold the roomId 
    roomIdToGetMessages = None
    
    for room in rooms:
        # Searches for the room "title" using the variable roomNameToSearch 
        if(room["title"].find(roomNameToSearch) != -1):

            # Displays the rooms found using the variable roomNameToSearch (additional options included)
            print ("Found rooms with the word " + roomNameToSearch)
            print(room["title"])

            # Stores room id and room title into variables
            roomIdToGetMessages = room["id"]
            roomTitleToGetMessages = room["title"]
            print("Found room : " + roomTitleToGetMessages)
            break

    if(roomIdToGetMessages == None):
        print("Sorry, I didn't find any room with " + roomNameToSearch + " in it.")
        print("Please try again...")
    else:
        break
 

def main():
    
    while True:
        
        # always add 1 second of delay to the loop to not go over a rate limit of API calls
        time.sleep(1)

        # the Webex Teams GET parameters
        #  "roomId" is is ID of the selected room
        #  "max": 1  limits to get only the very last message in the room
        GetParameters = {
                                "roomId": roomIdToGetMessages,
                                "max": 1
                             }
        
        # run the call against the messages endpoint of the Webex Teams API using the HTTP GET method
        r = requests.get("https://api.ciscospark.com/v1/messages", 
                             params = GetParameters, 
                             headers = {"Authorization": accessToken}
                        )
        # verify if the retuned HTTP status code is 200/OK
        if not r.status_code == 200:
            raise Exception( "Incorrect reply from Webex Teams API. Status code: {}. Text: {}".format(r.status_code, r.text))
        
        # get the JSON formatted returned data
        json_data = r.json()
        # check if there are any messages in the "items" array
        if len(json_data["items"]) == 0:
            raise Exception("There are no messages in the room.")
        
        # store the array of messages
        messages = json_data["items"]
        # store the text of the first message in the array
        message = messages[0]["text"]
        print("Received message: " + message)

        # check if the text of the message starts with the magic character "/gps" to start the bot
        if message.find("/gps") == 0:
            # Print Instructions to webex teams room
            Instructions = ("Geef je startlocatie op door '/start/' te typen, gevolgd door je locatie en land (bijvoorbeeld: /start/Brugge, Belgium)." +
                            "\nEen volledig adres geef je op volgende manier in: '/start/5,rijselstraat,brugge,belgium'" +
                            "\nTyp '/stop' om te stoppen (Typ vervolgens '/gps' om opnieuw te starten)."
                            )
            
            # the Webex Teams HTTP headers, including the Content-Type header for the POST JSON data
            HTTPHeaders = { 
                                 "Authorization": accessToken,
                                 "Content-Type": "application/json"
                               }
            # the Webex Teams POST JSON data
            #  "roomId" is is ID of the selected room
            #  "text": is the responseMessage assembled above
            PostInstructions = {
                                "roomId": roomIdToGetMessages,
                                "text" : Instructions
                            }
            # run the call against the messages endpoint of the Webex Teams API using the HTTP POST method
            #  Student Step #7
            #     Modify the code below to use the Webex Teams messages API endpoint (URL)
            r = requests.post( "https://api.ciscospark.com/v1/messages", 
                                  data = json.dumps(PostInstructions), 
                                  headers = HTTPHeaders
                             )
            while True:
                # always add 1 second of delay to the loop to not go over a rate limit of API calls
                time.sleep(1)

                # the Webex Teams GET parameters
                #  "roomId" is is ID of the selected room
                #  "max": 1  limits to get only the very last message in the room
                GetParameters = {
                                        "roomId": roomIdToGetMessages,
                                        "max": 1
                                     }
                
                # run the call against the messages endpoint of the Webex Teams API using the HTTP GET method
                r = requests.get("https://api.ciscospark.com/v1/messages", 
                                     params = GetParameters, 
                                     headers = {"Authorization": accessToken}
                                )
                # verify if the retuned HTTP status code is 200/OK
                if not r.status_code == 200:
                    raise Exception( "Incorrect reply from Webex Teams API. Status code: {}. Text: {}".format(r.status_code, r.text))
                
                # get the JSON formatted returned data
                json_data = r.json()
                # check if there are any messages in the "items" array
                if len(json_data["items"]) == 0:
                    raise Exception("There are no messages in the room.")
                
                # store the array of messages
                messages = json_data["items"]
                # store the text of the first message in the array
                message = messages[0]["text"]
                print("Received message: " + message)
                
                # /START/ Loop
                # Check for /start/
                if message.find("/stop") == 0:
                    main()
                if message.find("/start/") == 0:
                    orig = message[7:]
                    # Print Instructions to webex teams room
                    Instructions = "Geef je bestemming op door '/dest/' te typen, gevolgd door je locatie en land (bijvoorbeeld: /dest/Gent, Belgium)."
                    HTTPHeaders = { 
                                         "Authorization": accessToken,
                                         "Content-Type": "application/json"
                                   }
                    PostInstructions = {
                                        "roomId": roomIdToGetMessages,
                                        "text" : Instructions
                                        }
                    r = requests.post( "https://api.ciscospark.com/v1/messages", 
                                          data = json.dumps(PostInstructions), 
                                          headers = HTTPHeaders
                                     )
                    
                    while True:
                        # always add 1 second of delay to the loop to not go over a rate limit of API calls
                        time.sleep(1)

                        # the Webex Teams GET parameters
                        #  "roomId" is is ID of the selected room
                        #  "max": 1  limits to get only the very last message in the room
                        GetParameters = {
                                                "roomId": roomIdToGetMessages,
                                                "max": 1
                                             }
                        
                        # run the call against the messages endpoint of the Webex Teams API using the HTTP GET method
                        r = requests.get("https://api.ciscospark.com/v1/messages", 
                                             params = GetParameters, 
                                             headers = {"Authorization": accessToken}
                                        )
                        # verify if the retuned HTTP status code is 200/OK
                        if not r.status_code == 200:
                            raise Exception( "Incorrect reply from Webex Teams API. Status code: {}. Text: {}".format(r.status_code, r.text))
                        
                        # get the JSON formatted returned data
                        json_data = r.json()
                        # check if there are any messages in the "items" array
                        if len(json_data["items"]) == 0:
                            raise Exception("There are no messages in the room.")
                        
                        # store the array of messages
                        messages = json_data["items"]
                        # store the text of the first message in the array
                        message = messages[0]["text"]
                        print("Received message: " + message)
                        # /dest/ Loop
                        # Check for /dest/
                        if message.find("/stop") == 0:
                            main()
                        if message.find("/dest/") == 0:
                            dest = message[6:]
                            
                            # always add 1 second of delay to the loop to not go over a rate limit of API calls
                            time.sleep(1)    
                            # Mapquest URL 
                            main_api = "https://www.mapquestapi.com/directions/v2/route?"
                            url = main_api + urllib.parse.urlencode({"key": key, "from":orig, "to":dest})

                            json_data = requests.get(url).json()
                            #print(json.dumps(json_data, indent = 8))   
                            
                            json_status = json_data["info"]["statuscode"]

                            if json_status == 0:

                                # Print Directions to webex teams room
                                Directions = (
                                "API Status: " + str(json_status) + " = A successful route call."
                                "\n============================================="
                                "\nDirections from " + str(orig) + " to " + str(dest) +
                                "\nTrip Duration:   " + (json_data["route"]["formattedTime"]) +
                                "\nKilometers:      " + 
                            str("{:.2f}".format((json_data["route"]["distance"])*1.61)) +       
                                "\nFuel Used (Ltr): " + 
                            str("{:.2f}".format((json_data["route"]["fuelUsed"])*3.78)) +
                                "\n=============================================\n"
                                )
                                for each in json_data["route"]["legs"][0]["maneuvers"]:
                                    Directions+=((each["narrative"]) + " (" + str("{:.2f}".format((each["distance"])*1.61) + " km)\n"))

                                # the Webex Teams HTTP headers, including the Content-Type header for the POST JSON data
                                HTTPHeaders = { 
                                                     "Authorization": accessToken,
                                                     "Content-Type": "application/json"
                                }
                                # the Webex Teams POST JSON data
                                #  "roomId" is is ID of the selected room
                                #  "text": is the responseMessage assembled above
                                PostDirections = {
                                                    "roomId": roomIdToGetMessages,
                                                    "text" : Directions
                                }
                                # run the call against the messages endpoint of the Webex Teams API using the HTTP POST method
                                #  Student Step #7
                                #     Modify the code below to use the Webex Teams messages API endpoint (URL)
                                r = requests.post( "https://api.ciscospark.com/v1/messages", 
                                                      data = json.dumps(PostDirections), 
                                                      headers = HTTPHeaders
                                )
                                main()
                                
                            if not r.status_code == 200:
                                raise Exception("Incorrect reply from Webex Teams API. Status code: {}. Text: {}".format(r.status_code, r.text))
if __name__ == '__main__':
    main()                              
        


        
