from flask import jsonify
from werkzeug.exceptions import BadRequest, RequestEntityTooLarge
import logging

# Optional: setup logging to console
logger = logging.getLogger(__name__)

def register_error_handlers(app):
    @app.errorhandler(400)
    def handle_400(error):
        return jsonify({"error": "Permintaan tidak valid"}), 400

    @app.errorhandler(404)
    def handle_404(error):
        return jsonify({"error": "Endpoint tidak ditemukan"}), 404

    @app.errorhandler(500)
    def handle_500(error):
        logger.exception("Internal server error")  # log ke terminal
        return jsonify({"error": "Terjadi kesalahan di server"}), 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        logger.exception("Unhandled exception")  # log detailnya hanya di terminal
        return jsonify({"error": "Terjadi kesalahan tak terduga"}), 500
      
    @app.errorhandler(BadRequest)
    def handle_bad_request(e):
        return jsonify({"error": "Permintaan tidak valid (bad request)"}), 400

    @app.errorhandler(RequestEntityTooLarge)
    def handle_large_file(e):
        return jsonify({"error": "File terlalu besar"}), 413
