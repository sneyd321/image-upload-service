from server import celery
import base64
from firebase_admin import credentials, storage
import firebase_admin
import requests
from server.api.PDF import OntarioLease
from flask import Response
from server.api.RequestManager import Zookeeper, RequestManager

cred = credentials.Certificate(r'server/static/ServiceAccount.json')
firebase_admin.initialize_app(cred, {'storageBucket' : 'roomr-222721.appspot.com'})
bucket = storage.bucket()
bucket.versioning_enabled = False
bucket.clear_lifecyle_rules()
bucket.patch()
zookeeper = Zookeeper()

@celery.task()
def upload_image(problemId, imageString):
    global bucket
    blob = bucket.blob("Problems/Problem_" + str(problemId) + ".jpg")
    imageBytes = imageString.encode("utf-8")
    blob.upload_from_string(base64.b64decode(imageBytes), content_type="image/jpg")
    print("Complete")
    try:

        response = requests.put("http://problem-service.default.svc.cluster.local:8085/problem/v1/Problem/" + str(problemId) + "/imageURL", json={"imageURL": blob.public_url, "problemId": problemId})
        return blob.public_url

    except requests.exceptions.ConnectionError:
        return "Error could not connect to problem service"

@celery.task()
def build_ontario_lease(houseId, leaseData):
    global bucket
    homeownerId = None
    houseData = None
    homeownerData = None
    tenantData = None
    houseService = zookeeper.get_service("house-service")
    if houseService:
        houseManager = RequestManager(None, houseService)
        houseData = houseManager.get("house/v1/House/Tenant/" + str(houseId))
        homeownerId = houseData["homeownerId"]


    homeownerService = zookeeper.get_service("homeowner-service")
    if homeownerService and homeownerId:
        homeownerManager = RequestManager(None, homeownerService)
        homeownerData = homeownerManager.get("homeowner/v1/Homeowner/" + str(homeownerId))
   
    tenantService = zookeeper.get_service("tenant-service")
    if tenantService:
        tenantManager = RequestManager(None, tenantService)
        tenantData = tenantManager.get("tenant/v1/House/" + str(houseId) + "/Tenant")


    pdf = OntarioLease(leaseData, houseData, homeownerData, tenantData)
    pdfBytes = pdf.save_pdf()
  

    blob = bucket.blob("Lease/OntarioLeaseAgreementForHouseId_" + str(houseId) + ".pdf")
    if blob.exists():
        bucket.delete_blob("Lease/OntarioLeaseAgreementForHouseId_" + str(houseId) + ".pdf")
        blob = None
        blob = bucket.blob("Lease/OntarioLeaseAgreementForHouseId_" + str(houseId) + ".pdf")

    blob.upload_from_string(pdfBytes.getvalue(), content_type="application/pdf")

    documentService = zookeeper.get_service("document-service")
    if documentService:
        documentManager = RequestManager(None, documentService)

        status = documentManager.put("document/v1/House/" + str(houseId) + "/Province/Ontario/Document/Residential%20Tenancy%20Agreement%20%28Standard%20Form%20of%20Lease%29%20%28047%2D2229E%29", {"documentURL": blob.public_url})
        print(status)


    print("Complete")

    


        
@celery.task
def error_handler(request, exc, traceback):
    print('Task {0} raised exception: {1!r}\n{2!r}'.format(request.id, exc, traceback))
        