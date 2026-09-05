import os
import re
from config import TEMPLATE_DIR


class TemplateEngine:

    @staticmethod
    def render(request, template_name, context=None):

        if context is None:
            context = {}

        file_path = os.path.join(
            TEMPLATE_DIR,
            template_name
        )

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:
            html = file.read()
        # Handle FOR loops
        loop_pattern = re.compile(
            r"{%\s*for\s+(\w+)\s+in\s+(\w+)\s*%}"
            r"(.*?)"
            r"{%\s*endfor\s*%}",
            re.DOTALL
        )

        def render_loop(match):

            item_name = match.group(1)
            list_name = match.group(2)
            loop_html = match.group(3)

            items = context.get(
                list_name,
                []
            )

            result = ""

            for item in items:

                current_html = loop_html

                # Replace {{item[index]}}
                index_pattern = re.compile(
                    r"{{\s*"
                    + re.escape(item_name)
                    + r"\[(\d+)\]"
                    r"\s*}}"
                )

                def replace_index(index_match):

                    index = int(
                        index_match.group(1)
                    )

                    return str(
                        item[index]
                    )

                current_html = index_pattern.sub(
                    replace_index,
                    current_html
                )

                result += current_html

            return result


        html = loop_pattern.sub(
            render_loop,
            html
        )

        # Handle normal variables
        
        for key, value in context.items():

            if isinstance(value, (list, tuple)):
                continue

            html = html.replace(
                "{{" + key + "}}",
                str(value)
            )

        # Send response

        request.send_response(200)

        request.send_header(
            "Content-Type",
            "text/html"
        )

        request.end_headers()

        request.wfile.write(
            html.encode("utf-8")
        )