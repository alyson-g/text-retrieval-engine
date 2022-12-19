from typing import Tuple


def yield_sgml_text(file_name: str) -> Tuple[int, str]:
    """Yields document text from an SGML file.

    :param file_name: The name of the file
    :return: A tuple containing the unit of text contained within the SGML file
        and its identifier
    """
    with open(file_name, "r", encoding="utf-8") as file:
        document_id = None
        text = ""

        for line in file:
            if not line.isspace():
                if line.startswith("<P") or line.startswith("<Q"):
                    document_id = int(
                        line.replace("<P ID=", "").replace("<Q ID=", "").replace(">", "")
                    )
                elif "</P>" in line or "</Q>" in line:
                    yield document_id, text
                    document_id = None
                    text = ""
                else:
                    text += line
