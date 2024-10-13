import re
from pathlib import Path
from typing import Literal


def build_path(file_name: str) -> str:
    path = Path().absolute().joinpath(file_name)
    if path.exists():
        return path
    else:
        raise FileNotFoundError(path)


def file_manager(
    path: str,
    mode: Literal["r", "w"],
    text: str = "",
) -> list[str] | None:
    match mode:

        case "r":
            with open(path, mode) as f:
                data: list[str] = f.readlines()
            return data

        case "w":
            with open(path, mode) as f:
                f.write(text)


def extract_text_and_href(
    string: str,
    pattern: str = r"[\[\(](.*?)[\]\)]",
) -> list[str]:
    return re.findall(pattern, string)


def tag_generator(
    tag_type: Literal["heading", "list"],
    text: str,
    href: str = "",
    head_level: int = 0,
) -> list[str]:
    match tag_type:
        case "heading":
            return f"<h{head_level}>{text}</h{head_level}>"
        case "list":
            return (
                f"<li><a href='{href}' target='_blank' rel='noreferrer'>{text}</a></li>"
            )


def process_lines(data: list[str]):

    output = []
    for line in data:

        if line.startswith("#"):
            hash_count = line.count("#")
            text = line.replace("#", "").strip()
            tag = tag_generator("heading", text, head_level=hash_count)
            output.append(tag)

        elif line.startswith("-"):
            text, href = extract_text_and_href(line)
            tag = tag_generator("list", text, href)
            output.append(tag)

    return output


def insert_html_list_wrappers(data: list[str]) -> list[str]:

    for i in list(range(len(data) - 1)):

        if data[i].startswith("<h") and data[i + 1].startswith("<li>"):
            data.insert(i + 1, "<ul>")

        elif data[i].startswith("<li>") and data[i + 1].startswith("<h"):
            data.insert(i + 1, "</ul>")

    # Add ul to end
    data.append("</ul>")

    return data


def build_html(tags: list[str]) -> str:
    body_text: str = "".join(tags)
    return f"""<!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>😎 cool links</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
    </head>
    <body>
    {body_text}
    </body>
    </html>
    """


def main():

    SRC_NAME: str = "links.md"
    SRC_PATH: str = build_path(SRC_NAME)
    OUT_NAME: str = "index.html"
    OUT_PATH: str = build_path(OUT_NAME)

    data: list[str] = file_manager(SRC_PATH, mode="r")
    raw_tags: list[str] = process_lines(data)
    clean_tags: list[str] = insert_html_list_wrappers(raw_tags)
    html: str = build_html(clean_tags)

    # Save HTML to file
    file_manager(OUT_PATH, mode="w", text=html)


if __name__ == "__main__":
    main()
