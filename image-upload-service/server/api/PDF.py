from reportlab.pdfgen import canvas
from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger
import io


    
class OntarioLease:

    def __init__(self, leaseData, houseData, homeownerData, tenantData): 
        self._pdfReader = PdfFileReader('server/static/OntarioLeaseAgreementTemplate.pdf', strict=False)
        self._pdfWriter = PdfFileWriter()
        self.leaseData = leaseData
        self.tenantData = tenantData
        self.homeownerData = homeownerData
        self.houseData = houseData

       
    
    def getPageOneValues(self):
        pageOneValues = []
        if self.tenantData:
            try:
                if self.tenantData[0]:
                    pageOneValues.append((22, 342, self.tenantData[0]["lastName"]))
                    pageOneValues.append((365, 342, self.tenantData[0]["firstName"]))
                if self.tenantData[1]:
                    pageOneValues.append((22, 314, self.tenantData[1]["lastName"]))
                    pageOneValues.append((365, 314, self.tenantData[1]["firstName"]))
                if self.tenantData[2]:
                    pageOneValues.append((22, 287, self.tenantData[2]["lastName"]))
                    pageOneValues.append((365, 287, self.tenantData[2]["firstName"]))
                if self.tenantData[3]:
                    pageOneValues.append((22, 260, self.tenantData[3]["lastName"]))
                    pageOneValues.append((365, 260, self.tenantData[3]["firstName"]))
            except IndexError:
                pass
        
        pageOneValues.append((22, 447, self.homeownerData["firstName"] + " " + self.homeownerData["lastName"]))
        pageOneValues.append((22, 164, self.houseData["rentalUnitLocation"]["unitName"]))
        pageOneValues.append((220, 164, str(self.houseData["rentalUnitLocation"]["streetNumber"])))
        pageOneValues.append((310, 164, str(self.houseData["rentalUnitLocation"]["streetName"])))
        pageOneValues.append((22, 136, self.houseData["rentalUnitLocation"]["city"]))
        pageOneValues.append((310, 136, self.houseData["rentalUnitLocation"]['province']))
        pageOneValues.append((508, 136, self.houseData["rentalUnitLocation"]["postalCode"]))
        pageOneValues.append((22, 93, str(self.leaseData["rentDetails"]["parkingSpaces"])))
        pageOneValues.append((72, 56, "X") if self.houseData["rentalUnitLocation"]["isCondo"] else (22, 56, "X") )
        
        return pageOneValues

    def getPageTwoValues(self): 
       
        return [(22, 706, str(self.homeownerData["homeownerLocation"]["unitNumber"]))
        , (111, 706, str(self.homeownerData["homeownerLocation"]["streetNumber"]))
        , (201, 706,  self.homeownerData["homeownerLocation"]["streetName"])
        , (526, 706, self.homeownerData["homeownerLocation"]["poBox"])
        , (22, 679, self.homeownerData["homeownerLocation"]["city"])
        , (272, 679, self.homeownerData["homeownerLocation"]["province"])
        , (471, 679, self.homeownerData["homeownerLocation"]["postalCode"])
        , (22, 628, "X")
        , (22, 592, self.homeownerData["email"])
        , (22, 558, "X")
        , (22, 522, self.homeownerData["phoneNumber"])

        , (22, 395, "X")

        , (152, 258, self.leaseData["rentDetails"]["rentDueDate"])
        , (41, 237, "X")
        , (360, 172, "$" + str(round(self.leaseData["rentDetails"]["baseRent"], 2))) 
        , (360, 155, "$" + str(round(self.leaseData["rentDetails"]["parkingAmount"], 2)))
        , (360, 53, "$" + str(round(self.leaseData["rentDetails"]["baseRent"] + self.leaseData["rentDetails"]["parkingAmount"], 2)))
        ]

    def getPageThreeValues(self):
        pageThreeValues = []
        pageThreeValues.append((39, 692, self.leaseData["rentDetails"]["rentMadePayableTo"]))
        pageThreeValues.append((39, 648, "Cheque"))
        pageThreeValues.append((90, 648, "Cash"))
        pageThreeValues.append((158, 497, "20.00"))
        for amenity in self.leaseData["amenities"]:
            if amenity["name"] == "Gas":
                pageThreeValues.append((348, 386, "X")) if amenity["includedInRent"] else pageThreeValues.append((391, 386, "X"))
            if amenity["name"] == "Air Conditioning":
                pageThreeValues.append((348, 364, "X")) if amenity["includedInRent"] else pageThreeValues.append((391, 364, "X"))
            if amenity["name"] == "Storage":
                pageThreeValues.append((348, 343, "X")) if amenity["includedInRent"] else pageThreeValues.append((391, 343, "X"))
            if amenity["name"] == "On Site Laundry":
                pageThreeValues.append((348, 321, "X")) if amenity["includedInRent"] else pageThreeValues.append((391, 321, "X"))
                #pageThreeValues.append((420, 321, "X")) if amenity["payPerUse"] else pageThreeValues.append((391, 321, "X"))
            if amenity["name"] == "Guest Parking":
                pageThreeValues.append((348, 300, "X")) if amenity["includedInRent"] else pageThreeValues.append((391, 300, "X"))
                #pageThreeValues.append((420, 321, "X")) if amenity["payPerUse"] else pageThreeValues.append((391, 321, "X"))
        return pageThreeValues
        

    def getPageFourValues(self):
        pageFourValues = []
        for utility in self.leaseData['utilities']:
            if utility['name'] == "Electricity":
                pageFourValues.append((76, 729, "X") if utility["responsibilityOf"] == "Homeowner" else (148, 729, "X"))
            if utility['name'] == "Heat":
                pageFourValues.append((76, 707, "X") if utility["responsibilityOf"] == "Homeowner" else (148, 707, "X"))
            if utility['name'] == "Water":
                pageFourValues.append((76, 686, "X") if utility["responsibilityOf"] == "Homeowner" else (148, 686, "X"))
        pageFourValues.append((22, 402, "X"))
        pageFourValues.append((22, 163, "X"))
        return pageFourValues

    def getPageFiveValues(self):
        return [(22, 714, "X")
        , (22, 431, "X")
        , (22, 146, "X")
        ]

    def getPageSixValues(self):
        return [(22, 196, "X")]
    

    def createTextObject(self, canvas, x, y, text):
        textobject = canvas.beginText()
        textobject.setTextOrigin(x, y)
        textobject.textLine(text)
        return textobject

    def create_canvas_page(self, houseData):
        b = io.BytesIO()
        c = canvas.Canvas(b)
        for data in houseData:
            c.drawText(self.createTextObject(c, data[0], data[1], data[2]))
        c.showPage()
        c.save()
        canvasReader = PdfFileReader(b, strict=False)
        return canvasReader.getPage(0)

    def mergePage(self, pageValues, pageNumber):
        canvasPage = self.create_canvas_page(pageValues)
        leasePage = self._pdfReader.getPage(pageNumber)
        leasePage.mergePage(canvasPage)
        return leasePage

    def save_pdf(self):
        self._pdfWriter.addPage(self.mergePage(self.getPageOneValues(), 0))
        self._pdfWriter.addPage(self.mergePage(self.getPageTwoValues(), 1))
        self._pdfWriter.addPage(self.mergePage(self.getPageThreeValues(), 2))
        self._pdfWriter.addPage(self.mergePage(self.getPageFourValues(), 3))
        self._pdfWriter.addPage(self.mergePage(self.getPageFiveValues(), 4))
        self._pdfWriter.addPage(self.mergePage(self.getPageSixValues(), 5))
        for pageNumber in range(6, self._pdfReader.getNumPages()):
            self._pdfWriter.addPage(self._pdfReader.getPage(pageNumber))
        b = io.BytesIO()
        self._pdfWriter.write(b)
        return b

    

    








    

   

