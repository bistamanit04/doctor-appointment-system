import os
import re

from config import TEMPLATE_DIR


class TemplateEngine:

    @staticmethod
    def render(request, template_name, context=None):

        # --------------------------------
        # DEFAULT CONTEXT
        # --------------------------------

        if context is None:
            context = {}


        # --------------------------------
        # GET TEMPLATE FILE
        # --------------------------------

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


        # --------------------------------
        # HANDLE FOR LOOPS
        # Example:
        #
        # {% for doctor in doctors %}
        # {{doctor[0]}}
        # {{doctor[1]}}
        # {% endfor %}
        # --------------------------------

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
                # --------------------------------

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

                    try:
                        return str(
                            item[index]
                        )

                    except (IndexError, TypeError):

                        return ""


                current_html = index_pattern.sub(
                    replace_index,
                    current_html
                )


                # --------------------------------
                # HANDLE {{doctor}}
                # --------------------------------

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


        # Replace FOR loops first

        html = loop_pattern.sub(
            render_loop,
            html
        )


        # --------------------------------
        # HANDLE NORMAL VARIABLES
        #
        # Example:
        # {{title}}
        # {{error}}
        # {{name}}
        # --------------------------------

        variable_pattern = re.compile(
            r"{{\s*(\w+)\s*}}"
        )


        def replace_variable(match):

            key = match.group(1)

            value = context.get(
                key,
                ""
            )

            # Lists/tuples are handled by loops
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


        # --------------------------------
        # SEND HTTP RESPONSE
        # --------------------------------

        request.send_response(200)

        request.send_header(
            "Content-Type",
            "text/html; charset=utf-8"
        )

        request.end_headers()

        request.wfile.write(
            html.encode("utf-8")
        )

