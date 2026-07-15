import os
import mimetypes
from config import STATIC_DIR

class StaticController:

    @staticmethod
    def serve(request):

        relative_path = request.path.replace("/static/", "", 1)
        file_path = os.path.join(STATIC_DIR, relative_path)
        
        if not os.path.exists(file_path):
            request.send_error(404)
            return

        mime_type, _ = mimetypes.guess_type(file_path)

        if mime_type is None:
            mime_type = "application/octet-stream"

        request.send_response(200)
        request.send_header("Content-Type", mime_type)
        request.end_headers()

        with open(file_path, "rb") as file:
            request.wfile.write(file.read())