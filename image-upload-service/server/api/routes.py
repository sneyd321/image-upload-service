from flask import Flask, request, Response, jsonify
from . import image
import json, base64
from server.api.tasks import upload_image, error_handler, build_ontario_lease, upload_tenant_profile, upload_homeowner_profile
from server import celery
from celery.result import AsyncResult


            
@image.route("/Problem/<int:id>", methods=["POST"])
def upload_problem_image(id):
        if not request.files or "image" not in request.files:
            return Response("Error: Invalid Request")

        image = request.files["image"] 
        string = base64.b64encode(image.read())
        result = upload_image.apply_async((id, string.decode("utf-8")), countdown=5, link_error=error_handler.s())
        return Response(response=result.id, status=200)
  






@image.route("/Lease/Ontario/<int:houseId>", methods=["POST"])
def upload_lease(houseId):
    print(houseId)
    try:
        leaseData = request.get_json()
        result = build_ontario_lease.apply_async((houseId, leaseData), link_error=error_handler.s())
        return Response(response=result.id, status=201)
    except KeyError as e:
        return Response(response="Error: Invalid key entry " + str(e), status=400)





@image.route("/Homeowner/<int:homeownerId>/Profile", methods=["POST"])
def insert_homeowner_profile(homeownerId):
    try:
        print(request.files)
        image = request.files["image"] 
        string = base64.b64encode(image.read())
        result = upload_homeowner_profile.apply_async((homeownerId, string.decode("utf-8")), countdown=5, link_error=error_handler.s())
        return Response(response=result.id ,status=200)
    except KeyError as e:
        return Response(response="Error: Invalid key entry " + str(e), status=400)


@image.route("/Tenant/<int:tenantId>/Profile", methods=["POST"])
def insert_tenant_profile(tenantId):
    if not request.files or "image" not in request.files:
        return Response(response="Error: Bad Request Data", status=400)
    print(request.files)
    image = request.files["image"] 
    string = base64.b64encode(image.read())
    result = upload_tenant_profile.apply_async((tenantId, string.decode("utf-8")), countdown=5, link_error=error_handler.s())
    return Response(response=str(result.id), status=200)
 
        


@image.route("/House/<int:houseId>/Placeholder")
def upload_house_placeholder(houseId):
    pass


@image.route("/Task/<string:id>")
def get_task_state(id):
    return celery.AsyncResult(id).state

