import os
import re

from config import TEMPLATE_DIR


class TemplateEngine:

    @staticmethod
    def render(request, template_name, context=None):

        if context is None:
            context = {}

    
        # GET TEMPLAT

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


        # HANDLE FOR LOOPS
        #
        # {% for doctor in doctors %}
        # {{doctor[0]}}
        # {{doctor[1]}}
        # {{doctor[2]}}
        # {% endfor %}
      

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

                # --------------------------------
                # HANDLE {{doctor[0]}}
                # HANDLE {{doctor[1]}}
                # HANDLE {{doctor[2]}}
                # --------------------------------

                if isinstance(item, (list, tuple)):

                    index_pattern = re.compile(
                        r"{{\s*"
                        + re.escape(item_name)
                        + r"\s*\[\s*(\d+)\s*\]"
                        r"\s*}}"
                    )

                    def replace_index(index_match):

                        index = int(
                            index_match.group(1)
                        )

                        if index < len(item):

                            return str(
                                item[index]
                            )

                        return ""

                    current_html = index_pattern.sub(
                        replace_index,
                        current_html
                    )

                # HANDLE {{doctor}}
                

                simple_item_pattern = re.compile(
                    r"{{\s*"
                    + re.escape(item_name)
                    + r"\s*}}"
                )

                if not isinstance(
                    item,
                    (list, tuple, dict)
                ):

                    current_html = simple_item_pattern.sub(
                        str(item),
                        current_html
                    )

                result += current_html

            return result

      
        # PROCESS LOOPS
        html = loop_pattern.sub(
            render_loop,
            html
        )

        # NORMAL VARIABLES
        # {{title}}
        # {{error}}
   

        variable_pattern = re.compile(
            r"{{\s*(\w+)\s*}}"
        )

        def replace_variable(match):

            key = match.group(1)

            value = context.get(
                key,
                ""
            )

            if isinstance(
                value,
                (list, tuple)
            ):

                return ""

            return str(value)

        html = variable_pattern.sub(
            replace_variable,
            html
        )

     
        # SEND RESPONSE
        request.send_response(200)

        request.send_header(
            "Content-Type",
            "text/html; charset=utf-8"
        )

        request.end_headers()

        request.wfile.write(
            html.encode("utf-8")
        )