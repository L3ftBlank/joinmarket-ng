"""MkDocs Hook"""

import re

def on_page_markdown(markdown, page, config, files, **kwargs):
    markdown = re.sub(r"\]\(\./taker/README\.md\)", "](README_taker.md)", markdown)
    markdown = re.sub(r"\]\(\./maker/README\.md\)", "](README_maker.md)", markdown)
    return markdown
