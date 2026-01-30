from flask_cors import CORS

def init_cors(app):
    # Cho phép frontend gửi header Authorization (JWT Bearer token)
    CORS(
        app,
        resources={r"/*": {
            "origins": "*",
            "allow_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["Content-Type"],
        }},
    )
    return app