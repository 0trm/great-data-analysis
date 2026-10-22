# Build the page at 0trm.dev/good-data-analysis/ from README.md.
# Run from the repo root: python3 site/build.py  (needs markdown-it-py); it writes _site/.

# %%
import pathlib
import re
import shutil

from markdown_it import MarkdownIt

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
OUT = ROOT / "_site"
ASSETS = ["favicon.svg", "favicon.ico", "apple-touch-icon.png"]


def slug(text):
    # GitHub's anchor rule, so the README's own #technical links keep working
    return re.sub(r"[^\w\- ]", "", text.strip().lower()).replace(" ", "-")


# %%
md = MarkdownIt("commonmark").enable("table")
tokens = md.parse((ROOT / "README.md").read_text())

heads = []  # (level, text, id) for every h2 and h3
for i, token in enumerate(tokens):
    if token.type == "heading_open":
        text = "".join(c.content for c in tokens[i + 1].children if c.type in ("text", "code_inline"))
        token.attrSet("id", slug(text))
        if token.tag in ("h2", "h3"):
            heads.append((int(token.tag[1]), text, slug(text)))

# %%
# Number the sections that hold habits (1 Technical ... 4 Agents) and each habit in them (1.1 ...);
# Closing and Attribution hold none and stay unnumbered
holds_habits = {hid for k, (level, _, hid) in enumerate(heads) if level == 2 and k + 1 < len(heads) and heads[k + 1][0] == 3}
numbers, section, habit = {}, 0, 0
for level, _, hid in heads:
    if level == 2 and hid in holds_habits:
        section, habit = section + 1, 0
        numbers[hid] = str(section)
    elif level == 3:
        habit += 1
        numbers[hid] = f"{section}.{habit}"

content = md.renderer.render(tokens, md.options, {})
content = re.sub(
    r'<h([23]) id="([^"]+)">',
    lambda m: m.group(0) + (f'<span class="no">{numbers[m.group(2)]}</span> ' if m.group(2) in numbers else ""),
    content,
)
# Links off the page open in a new tab; the page's own #anchors stay in it
content = content.replace('<a href="http', '<a target="_blank" rel="noopener" href="http')

toc = "\n".join(
    f'      <li class="l{level}"><a href="#{hid}"><span class="no">{numbers.get(hid, "")}</span> {text}</a></li>'
    for level, text, hid in heads
)

# %%
OUT.mkdir(exist_ok=True)
page = (SITE / "template.html").read_text().replace("{{toc}}", toc).replace("{{content}}", content)
(OUT / "index.html").write_text(page)
for name in ASSETS:
    shutil.copy(SITE / name, OUT / name)
print(f"_site/index.html: {len(heads)} headings, {len(numbers)} numbered")
