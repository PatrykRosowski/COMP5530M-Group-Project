class AccessNode:
    def __init__(self, data_row):
        self.ATCOCode = data_row["ATCOCode"]
        self.CommonName = data_row["CommonName"]
        self.Street = data_row["Street"]
        self.Longitude = data_row["Longitude"]
        self.Latitude = data_row["Latitude"]
        self.Nearby = []

    def get_ATCOCode(self):
        return self.ATCOCode

    def get_CommonName(self):
        return self.CommonName

    def get_Street(self):
        return self.Street

    def get_Longitude(self):
        return self.Longitude

    def get_Latitude(self):
        return self.Latitude

    def get_Nearby(self):
        return self.Nearby

    def addNearbyStop(self, nearbyStop):
        ## Check if nearby stop is already in the list
        if not nearbyStop in self.Nearby:
            self.Nearby.append(nearbyStop)
