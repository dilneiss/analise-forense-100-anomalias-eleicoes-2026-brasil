import json

with open("apresentacao_slides.html", "r", encoding="utf-8") as f:
    text = f.read()

s_start = text.find("const SLIDES = ") + len("const SLIDES = ")
s_end = text.find(";\n\n        let currentSlideIdx", s_start)
slides = json.loads(text[s_start:s_end].strip())

s6 = slides[5]
assert s6["id"] == 6

vh = s6["visual_html"]

# Replace the max-height and overflow-y: auto in s6 visual_html
old_container_str = 'max-height: clamp(140px, 20vh, 195px); overflow-y: auto; padding-right: 2px;'
assert old_container_str in vh

new_container_str = 'padding-right: 2px;'

s6["visual_html"] = vh.replace(old_container_str, new_container_str)

slides_json_str = json.dumps(slides, ensure_ascii=False)
full_html = text[:s_start] + slides_json_str + text[s_end:]

with open("apresentacao_slides.html", "w", encoding="utf-8") as f:
    f.write(full_html)

with open("comparison_nacional_brasil/apresentacao_slides.html", "w", encoding="utf-8") as f:
    f.write(full_html)

print("Slide 6 scroll removed successfully!")
