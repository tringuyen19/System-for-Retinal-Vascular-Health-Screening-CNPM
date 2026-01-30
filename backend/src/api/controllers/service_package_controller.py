from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from api.middleware.auth_middleware import require_roles, require_role
from infrastructure.repositories.service_package_repository import ServicePackageRepository
from infrastructure.databases.mssql import session
from services.service_package_service import ServicePackageService
from api.responses import success_response, error_response, not_found_response, validation_error_response
from api.schemas import ServicePackageCreateRequestSchema, ServicePackageUpdateRequestSchema, ServicePackageResponseSchema

service_package_bp = Blueprint('service_package', __name__, url_prefix='/api/service-packages')

# Initialize repository (only for service initialization)
package_repo = ServicePackageRepository(session)

# Initialize SERVICE (Business Logic Layer) ✅
package_service = ServicePackageService(package_repo)


@service_package_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    ---
    tags:
      - Service Package
    responses:
      200:
        description: Service is healthy
    """
    return success_response({"status": "healthy"}, "Service Package service is running")


@service_package_bp.route('', methods=['POST'])
@require_role('Admin')
def create_package():
    """
    Create a new service package
    ---
    tags:
      - Service Package
    security:
      - Bearer: []
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
            - price
            - image_limit
            - duration_days
          properties:
            name:
              type: string
              example: "Premium Package"
            price:
              type: number
              format: float
              example: 99000.00
            image_limit:
              type: integer
              example: 100
            duration_days:
              type: integer
              example: 30
    responses:
      201:
        description: Package created successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Package created successfully
            data:
              type: object
      400:
        description: Invalid input
    """
    try:
        schema = ServicePackageCreateRequestSchema()
        data = schema.load(request.get_json())
        
        # Check if name exists via SERVICE
        existing = package_service.get_package_by_name(data['name'])
        if existing:
            return error_response('Package name already exists', 400)
        
        package = package_service.create_package(
            name=data['name'],
            price=float(data['price']),
            image_limit=int(data['image_limit']),
            duration_days=int(data['duration_days'])
        )
        
        response_schema = ServicePackageResponseSchema()
        return success_response(response_schema.dump(package), 'Package created successfully', 201)
        
    except ValidationError as e:
        return validation_error_response(e.messages)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@service_package_bp.route('/<int:package_id>', methods=['GET'])
def get_package(package_id):
    """
    Get package by ID
    ---
    tags:
      - Service Package
    parameters:
      - name: package_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Package found
      404:
        description: Package not found
    """
    try:
        package = package_service.get_package_by_id(package_id)
        if not package:
            return not_found_response('Package not found')
        
        schema = ServicePackageResponseSchema()
        return success_response(schema.dump(package))
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@service_package_bp.route('/name/<name>', methods=['GET'])
def get_package_by_name(name):
    """
    Get package by name
    ---
    tags:
      - Service Package
    parameters:
      - name: name
        in: path
        required: true
        schema:
          type: string
    responses:
      200:
        description: Package found
      404:
        description: Package not found
    """
    try:
        package = package_service.get_package_by_name(name)
        if not package:
            return not_found_response('Package not found')
        
        schema = ServicePackageResponseSchema()
        return success_response(schema.dump(package))
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@service_package_bp.route('', methods=['GET'])
def get_all_packages():
    """
    Get all service packages
    ---
    tags:
      - Service Package
    parameters:
      - name: min_price
        in: query
        required: false
        schema:
          type: number
      - name: max_price
        in: query
        required: false
        schema:
          type: number
    responses:
      200:
        description: List of packages
    """
    try:
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        
        if min_price is not None and max_price is not None:
            # Filter by price range (need to add to service or filter in controller)
            all_packages = package_service.list_all_packages()
            packages = [p for p in all_packages if min_price <= float(p.price) <= max_price]
        else:
            packages = package_service.list_all_packages()
        
        return success_response({
            'count': len(packages),
            'packages': [{
                'package_id': p.package_id,
                'name': p.name,
                'price': float(p.price),
                'image_limit': p.image_limit,
                'duration_days': p.duration_days
            } for p in packages]
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@service_package_bp.route('/cheapest', methods=['GET'])
def get_cheapest():
    """
    Get cheapest package
    ---
    tags:
      - Service Package
    responses:
      200:
        description: Cheapest package
      404:
        description: No packages found
    """
    try:
        package = package_service.get_cheapest_package()
        if not package:
            return not_found_response('No packages found')
        
        schema = ServicePackageResponseSchema()
        return success_response(schema.dump(package))
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@service_package_bp.route('/premium', methods=['GET'])
def get_most_expensive():
    """
    Get most expensive/premium package
    ---
    tags:
      - Service Package
    responses:
      200:
        description: Most expensive package
      404:
        description: No packages found
    """
    try:
        package = package_service.get_most_expensive_package()
        if not package:
            return not_found_response('No packages found')
        
        schema = ServicePackageResponseSchema()
        return success_response(schema.dump(package))
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@service_package_bp.route('/<int:package_id>', methods=['PUT'])
@require_role('Admin')
def update_package(package_id):
    """
    Update package
    ---
    tags:
      - Service Package
    security:
      - Bearer: []
    parameters:
      - name: package_id
        in: path
        required: true
        schema:
          type: integer
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: package_id
        in: path
        required: true
        schema:
          type: integer
          example: 1
      - in: body
        name: body
        required: false
        schema:
          type: object
          properties:
            name:
              type: string
              example: "Updated Package Name"
            price:
              type: number
              format: float
              example: 149000.00
            image_limit:
              type: integer
              example: 200
            duration_days:
              type: integer
              example: 60
    responses:
      200:
        description: Package updated successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Package updated successfully
            data:
              type: object
      404:
        description: Package not found
    """
    try:
        data = request.get_json()
        
        # If updating name, check if it already exists
        if data.get('name'):
            existing = package_service.get_package_by_name(data['name'])
            if existing and existing.package_id != package_id:
                return error_response('Package name already exists', 400)
        
        package = package_service.update_package(package_id, **data)
        if not package:
            return not_found_response('Package not found')
        
        return success_response({
            'package_id': package.package_id,
            'name': package.name,
            'price': float(package.price),
            'image_limit': package.image_limit,
            'duration_days': package.duration_days
        }, 'Package updated successfully')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@service_package_bp.route('/<int:package_id>/price', methods=['PUT'])
@require_role('Admin')
def update_price(package_id):
    """
    Update package price
    ---
    tags:
      - Service Package
    security:
      - Bearer: []
    parameters:
      - name: package_id
        in: path
        required: true
        schema:
          type: integer
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: package_id
        in: path
        required: true
        schema:
          type: integer
          example: 1
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - price
          properties:
            price:
              type: number
              format: float
              example: 199000.00
    responses:
      200:
        description: Price updated
        schema:
          type: object
          properties:
            message:
              type: string
              example: Price updated successfully
            data:
              type: object
      400:
        description: Price is required
      404:
        description: Package not found
    """
    try:
        data = request.get_json()
        if not data.get('price'):
            return validation_error_response({'price': 'Price is required'})
        
        package = package_service.update_price(package_id, float(data['price']))
        if not package:
            return not_found_response('Package not found')
        
        return success_response({
            'package_id': package.package_id,
            'price': float(package.price)
        }, 'Price updated successfully')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@service_package_bp.route('/<int:package_id>', methods=['DELETE'])
@require_role('Admin')
def delete_package(package_id):
    """
    Delete package
    ---
    tags:
      - Service Package
    security:
      - Bearer: []
    parameters:
      - name: package_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Package deleted successfully
      404:
        description: Package not found
    """
    try:
        result = package_service.delete_package(package_id)
        if not result:
            return not_found_response('Package not found')
        
        return success_response(None, 'Package deleted successfully')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@service_package_bp.route('/stats', methods=['GET'])
@require_roles(['Admin', 'ClinicManager'])
def get_stats():
    """
    Get package statistics
    ---
    tags:
      - Service Package
    security:
      - Bearer: []
    responses:
      200:
        description: Package statistics
    """
    try:
        stats = package_service.get_package_statistics()
        
        return success_response({
            'total_packages': stats.get('total', 0),
            'average_price': round(stats.get('average_price', 0), 2)
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)

