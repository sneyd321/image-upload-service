from flask import Flask, request, Response, jsonify
from . import image
import json, base64
from server.api.tasks import upload_image, error_handler, build_ontario_lease



            
@image.route("/Problem/<int:id>", methods=["POST"])
def upload_problem_image(id):
    try:
        print(request.files)

        image = request.files["image"] 
        string = base64.b64encode(image.read())
        upload_image.apply_async((id, string.decode("utf-8")), countdown=5, link_error=error_handler.s())
        return Response(status=200)
    except KeyError as e:
        return Response(response="Error: Invalid key entry " + str(e), status=400)






@image.route("/Lease/Ontario/<int:houseId>", methods=["POST"])
def upload_lease(houseId):
    print(houseId)
    leaseData = request.get_json()
    build_ontario_lease.apply_async((houseId, leaseData), link_error=error_handler.s())
    return Response(response="FormComplete", status=201)
    





@image.route("/Homeowner/<int:homeownerId>/Profile")
def upload_homeowner_profile(homeownerId):
    pass


@image.route("/Tenant/<int:tenantId>/Profile")
def upload_tenant_profile(tenantId):
    pass


@image.route("/House/<int:houseId>/Placeholder")
def upload_house_placeholder(houseId):
    pass




