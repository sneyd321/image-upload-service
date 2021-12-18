from server import celery
from firebase_admin import credentials, storage
import firebase_admin
import requests, time, base64
from server.api.PDF import OntarioLease
from flask import Response
from server.api.RequestManager import Zookeeper, RequestManager

cred = credentials.Certificate(r'server/static/ServiceAccount.json')
firebase_admin.initialize_app(cred, {'storageBucket' : 'roomr-222721.appspot.com'})
bucket = storage.bucket()

zookeeper = Zookeeper()

@celery.task()
def upload_image(problemId, imageString):
    notificationService = zookeeper.get_service("notification-service")
    if notificationService:
        notificationManager = RequestManager(None, notificationService)
        print("PENDING")
        print(notificationManager.post("notification/v1/Problem/" + str(problemId), { "state": "PENDING" } ))
    else:
        print("notification service unavailable")


    global bucket
    blob = bucket.blob("Problems/Problem_" + str(problemId) + ".jpg")
    imageBytes = imageString.encode("utf-8")
    blob.upload_from_string(base64.b64decode(imageBytes), content_type="image/jpg")
    
    problemService = zookeeper.get_service("problem-service")
    if problemService:
        manager = RequestManager(None, problemService)
        print(manager.put("problem/v1/Problem/" + str(problemId) + "/imageURL", {"imageURL": blob.public_url, "problemId": problemId}))
        if notificationService:
            notificationManager = RequestManager(None, notificationService)
            print("SUCCESS")
            print(notificationManager.post("notification/v1/Problem/" + str(problemId), { "state": "SUCCESS" } ))
    else:
        if notificationService:
            notificationManager = RequestManager(None, notificationService)
            print("FAILURE")
            print(notificationManager.post("notification/v1/Problem/" + str(problemId), { "state": "FAILURE" } ))

    if notificationService:
        notificationManager = RequestManager(None, notificationService)
        print(notificationManager.post("notification/v1/Problem/" + str(problemId), { "state": "COMPLETE" } ))

    print("COMPLETE")
    

@celery.task()
def build_ontario_lease(houseId, leaseData):
    global bucket
    homeownerId = 0
    houseData = {}
    homeownerData = {}
    tenantData = {}

    print(leaseData)

    houseService = zookeeper.get_service("house-service")
    if houseService:
        houseManager = RequestManager(None, houseService)
        houseData = houseManager.get("house/v1/House/" + str(houseId) + "/Tenant")
        print(houseData)
        homeownerId = houseData["homeownerId"]

    notificationService = zookeeper.get_service("notification-service")
    if notificationService:
        notificationManager = RequestManager(None, notificationService)
        print("PENDING")
        print(notificationManager.post("notification/v1/Homeowner/" + str(homeownerId) + "/Lease/Ontario", { "state": "PENDING" } ))
    else:
        print("notification service unavailable")


    homeownerService = zookeeper.get_service("homeowner-service")
    if homeownerService and homeownerId:
        homeownerManager = RequestManager(None, homeownerService)
        
        homeownerData = homeownerManager.get("homeowner/v1/Homeowner/" + str(homeownerId))
        print(homeownerData)
   
    tenantService = zookeeper.get_service("tenant-service")
    if tenantService:
        tenantManager = RequestManager(None, tenantService)
        tenantData = tenantManager.get("tenant/v1/House/" + str(houseId) + "/Tenant")
        print(tenantData)

    try:
        pdf = OntarioLease(leaseData, houseData, homeownerData, tenantData)
        pdfBytes = pdf.save_pdf()
    except KeyError as e:
        if notificationService:
            print("FAILURE (KEY ERROR)" + str(e))
            notificationManager = RequestManager(None, notificationService)
            print(notificationManager.post("notification/v1/Homeowner/" + str(homeownerId) + "/Lease/Ontario", { "state": "FAILURE" } ))
        return
  
    
    blob = bucket.blob("Lease/OntarioLeaseAgreementForHouseId_" + str(houseId) + ".pdf")
    blob.cache_control = "no-cache"
    if blob.exists():
        bucket.delete_blob("Lease/OntarioLeaseAgreementForHouseId_" + str(houseId) + ".pdf")
        blob = None
        blob = bucket.blob("Lease/OntarioLeaseAgreementForHouseId_" + str(houseId) + ".pdf")
        blob.cache_control = "no-cache"

    blob.upload_from_string(pdfBytes.getvalue(), content_type="application/pdf")

    documentService = zookeeper.get_service("document-service")
    if documentService:
        documentManager = RequestManager(None, documentService)

        status = documentManager.put("document/v1/House/" + str(houseId) + "/Province/Ontario/Document/Residential%20Tenancy%20Agreement%20%28Standard%20Form%20of%20Lease%29%20%28047%2D2229E%29", {"documentURL": blob.public_url})
        print(status)
        if notificationService:
            notificationManager = RequestManager(None, notificationService)
            print("SUCCESS")
            print(notificationManager.post("notification/v1/Homeowner/" + str(homeownerId) + "/Lease/Ontario", { "state": "SUCCESS" } ))
    else:
        if notificationService:
            print("FAILURE")
            notificationManager = RequestManager(None, notificationService)
            print(notificationManager.post("notification/v1/Homeowner/" + str(homeownerId) + "/Lease/Ontario", { "state": "FAILURE" } ))


    if notificationService:
        notificationManager = RequestManager(None, notificationService)
        print(notificationManager.post("notification/v1/Homeowner/" + str(homeownerId) + "/Lease/Ontario", { "state": "COMPLETE" } ))


    

    print("Complete")

    
@celery.task()
def upload_tenant_profile(tenantId, imageString):
    notificationService = zookeeper.get_service("notification-service")
    if notificationService:
        notificationManager = RequestManager(None, notificationService)
        print("PENDING")
        print(notificationManager.post("notification/v1/Tenant/" + str(tenantId) + "/Profile", { "state": "PENDING" } ))
    else:
        print("notification service unavailable")

    imageBytes = imageString.encode("utf-8")
    blob = bucket.blob("Profiles/Tenant/Tenant_" + str(tenantId) + ".jpg")
    blob.cache_control = "no-cache"
    if blob.exists():
        blob.delete()
        blob = None

        blob = bucket.blob("Profiles/Tenant/Tenant_" + str(tenantId) + ".jpg")
        blob.cache_control = "no-cache"
        blob.upload_from_string(base64.b64decode(imageBytes), content_type="image/jpg")

        
    else:
        blob.upload_from_string(base64.b64decode(imageBytes), content_type="image/jpg")
    


    tenantService = zookeeper.get_service("tenant-service")
    if tenantService:
        manager = RequestManager(None, tenantService)
        print(manager.put("tenant/v1/Tenant/" + str(tenantId) + "/imageURL", {"imageURL": blob.public_url, "tenantId": tenantId}))
        if notificationService:
            notificationManager = RequestManager(None, notificationService)
            print("SUCCESS")
            print(notificationManager.post("notification/v1/Tenant/" + str(tenantId) + "/Profile", { "state": "SUCCESS" } ))
    else:
        if notificationService:
            notificationManager = RequestManager(None, notificationService)
            print("FAILURE")
            print(notificationManager.post("notification/v1/Tenant/" + str(tenantId) + "/Profile", { "state": "FAILURE" } ))
        
    if notificationService:
        notificationManager = RequestManager(None, notificationService)
        print(notificationManager.post("notification/v1/Tenant/" + str(tenantIdcd) + "/Profile", { "state": "COMPLETE" } ))

    print("Complete")



@celery.task()
def upload_homeowner_profile(homeownerId, imageString):
    notificationService = zookeeper.get_service("notification-service")
    if notificationService:
        notificationManager = RequestManager(None, notificationService)
        print("PENDING")
        print(notificationManager.post("notification/v1/Homeowner/" + str(homeownerId) + "/Profile", { "state": "PENDING" } ))
    else:
        print("notification service unavailable")

    imageBytes = imageString.encode("utf-8")
    blob = bucket.blob("Profiles/Homeowner/Homeowner_" + str(homeownerId) + ".jpg")
    blob.cache_control = "no-cache"
    if blob.exists():
        blob.delete()
        blob = None

        blob = bucket.blob("Profiles/Homeowner/Homeowner_" + str(homeownerId) + ".jpg")
        blob.upload_from_string(base64.b64decode(imageBytes), content_type="image/jpg")
        blob.cache_control = "no-cache"
        
    else:
        blob.upload_from_string(base64.b64decode(imageBytes), content_type="image/jpg")


    homeownerService = zookeeper.get_service("homeowner-service")
    if homeownerService:
        manager = RequestManager(None, homeownerService)
        print(manager.put("homeowner/v1/Homeowner/" + str(homeownerId) + "/imageURL", { "imageURL": blob.public_url }))
        if notificationService:
            notificationManager = RequestManager(None, notificationService)
            print("SUCCESS")
            print(notificationManager.post("notification/v1/Homeowner/" + str(homeownerId) + "/Profile", { "state": "SUCCESS" } ))
    else:
        if notificationService:
            print("FAILURE")
            notificationManager = RequestManager(None, notificationService)
            print(notificationManager.post("notification/v1/Homeowner/" + str(homeownerId) + "/Profile", { "state": "FAILURE" } ))


    if notificationService:
        notificationManager = RequestManager(None, notificationService)
        print(notificationManager.post("notification/v1/Homeowner/" + str(homeownerId) + "/Profile", { "state": "COMPLETE" } ))


    
    print("Complete")

        
@celery.task
def error_handler(request, exc, traceback):
    print('Task {0} raised exception: {1!r}\n{2!r}'.format(request.id, exc, traceback))
        