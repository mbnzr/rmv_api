import requests
import json
import time
from datetime import datetime


class RMV_API():
    def __init__(self, accessID, response_format="json"):
        self.accessID = accessID
        self.response_format = response_format


class Station():
    def __init__(self, api_token, hafas_ID="3000010"):
        self.api_token = api_token
        self.hafas_ID = hafas_ID

    def query_departures(self):
        paramters = {"accessId": self.api_token.accessID, "extId": self.hafas_ID,
                     "format": self.api_token.response_format, "rtMode": "REALTIME"}
        try:
            self.response = requests.get("https://www.rmv.de/hapi/DepartureBoard", params=paramters)
            self.response_json = json.loads(self.response.content)
            return(self.response.status_code)
        except requests.exceptions.Timeout:
            print("Timeout connecting to server")
        except requests.exceptions.TooManyRedirects:
            print("Cant reach server. Bad URL?")
        except requests.exceptions.RequestException as e:
            print(e)
            sys.exit(1)

    def get_next_rides(self):
        if self.response.status_code == 200:
            self.next_rides = []
            for connection in self.response_json['Departure']:
                try:
                    rtTime_DT = datetime.strptime(connection["rtDate"] + connection["rtTime"], "%Y-%m-%d%H:%M:%S")
                    if rtTime_DT > datetime.now():
                        rtDiff = rtTime_DT - datetime.now()
                        self.next_rides.append((connection["Product"]["line"], connection["rtTime"], rtDiff.seconds))
                except KeyError:
                    pass
            return(self.next_rides)
        else:
            print("HTTP Error: %s" % self.response.status_code)


rmv_api = RMV_API("ddd808ab-68df-4630-a566-db570dc011d9")
merianplatz = Station(rmv_api, "3000512")
merianplatz.query_departures()

while merianplatz.get_next_rides()[0][2] > 0:
    print("%s departures at %s in %d seconds" % merianplatz.next_rides[0])
    time.sleep(1)
