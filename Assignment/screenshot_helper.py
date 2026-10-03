import os
import re
import json
from PIL import Image, ImageDraw, ImageFont

SCREENSHOTS_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

FONT_PATH = "C:/Windows/Fonts/consola.ttf"
FONT_BOLD_PATH = "C:/Windows/Fonts/consolab.ttf"
FONT_UI_PATH = "C:/Windows/Fonts/segoeui.ttf"
FONT_UI_BOLD_PATH = "C:/Windows/Fonts/segoeuib.ttf"

def get_fonts(size=14):
    try:
        font = ImageFont.truetype(FONT_PATH, size)
        font_bold = ImageFont.truetype(FONT_BOLD_PATH, size)
        font_ui = ImageFont.truetype(FONT_UI_PATH, size)
        font_ui_bold = ImageFont.truetype(FONT_UI_BOLD_PATH, size)
    except:
        font = font_bold = font_ui = font_ui_bold = ImageFont.load_default()
    return font, font_bold, font_ui, font_ui_bold

def render_terminal_screenshot(filename, title, command, output_lines, width=1050):
    font, font_bold, font_ui, font_ui_bold = get_fonts(14)
    line_height = 21
    header_height = 36
    padding = 20

    all_lines = []
    if command:
        all_lines.append(("cmd", f"$ {command}"))
        all_lines.append(("blank", ""))

    for line in output_lines:
        line_str = str(line)
        while len(line_str) > 115:
            all_lines.append(("text", line_str[:115]))
            line_str = "  " + line_str[115:]
        all_lines.append(("text", line_str))

    total_height = header_height + padding * 2 + len(all_lines) * line_height + 10
    total_height = max(total_height, 120)

    img = Image.new("RGBA", (width, total_height), (30, 30, 46, 255))
    draw = ImageDraw.Draw(img)

    # Title bar
    draw.rectangle([(0, 0), (width, header_height)], fill=(24, 24, 37, 255))
    draw.line([(0, header_height), (width, header_height)], fill=(49, 50, 68, 255), width=1)

    # Window dots
    draw.ellipse([(14, 12), (24, 22)], fill=(243, 139, 168, 255))
    draw.ellipse([(32, 12), (42, 22)], fill=(249, 226, 175, 255))
    draw.ellipse([(50, 12), (60, 22)], fill=(166, 227, 161, 255))

    # Title
    draw.text((width // 2 - len(title) * 4, 9), title, font=font_bold, fill=(205, 214, 244, 255))

    y = header_height + padding
    for ltype, line in all_lines:
        if ltype == "cmd":
            draw.text((padding, y), line, font=font_bold, fill=(137, 220, 235, 255))
        elif ltype == "blank":
            pass
        else:
            color = (205, 214, 244, 255)
            if any(k in line for k in ["BUILD SUCCESS", "healthy", "200 OK", "201 Created", "PASS", "True", "Exited (0)", "ACTIVE", "CONFIRMED"]):
                color = (166, 227, 161, 255)
            elif any(k in line for k in ["ERROR", "FAILURE", "401", "403", "404", "409", "500", "503", "FAIL", "CANCELLED", "INACTIVE"]):
                color = (243, 139, 168, 255)
            elif any(k in line for k in ["WARN", "SCHEDULED"]):
                color = (249, 226, 175, 255)
            elif line.startswith("[INFO]") or line.startswith("-->") or line.startswith("==="):
                color = (137, 180, 250, 255)
            elif any(k in line for k in ["SELECT", "DATABASE", "TABLE", "HTTP", "POST", "GET", "PUT", "DELETE", "ObjectId"]):
                color = (203, 166, 247, 255)

            draw.text((padding, y), line, font=font, fill=color)

        y += line_height

    filepath = os.path.join(SCREENSHOTS_DIR, filename)
    img.save(filepath, "PNG")
    return filepath

def render_postman_screenshot(filename, request_name, method, url, status_code, response_body="", test_results=None, width=1050):
    font, font_bold, font_ui, font_ui_bold = get_fonts(14)
    header_height = 42
    bar_height = 50
    padding = 20
    line_height = 20

    # Format JSON response if possible
    body_lines = []
    if response_body:
        try:
            if isinstance(response_body, str):
                parsed = json.loads(response_body)
                formatted = json.dumps(parsed, indent=2, ensure_ascii=False)
            else:
                formatted = json.dumps(response_body, indent=2, ensure_ascii=False)
            for l in formatted.split("\n"):
                body_lines.append(l)
        except:
            for l in str(response_body).split("\n"):
                body_lines.append(l)

    # Test lines
    test_lines = test_results or []

    content_lines_count = len(body_lines) + (len(test_lines) + 2 if test_lines else 0)
    total_height = header_height + bar_height + padding * 2 + content_lines_count * line_height + 30
    total_height = max(total_height, 220)

    img = Image.new("RGBA", (width, total_height), (24, 24, 37, 255))
    draw = ImageDraw.Draw(img)

    # Top Bar (Postman Title)
    draw.rectangle([(0, 0), (width, header_height)], fill=(17, 17, 27, 255))
    draw.line([(0, header_height), (width, header_height)], fill=(49, 50, 68, 255), width=1)

    # Dots
    draw.ellipse([(14, 15), (24, 25)], fill=(243, 139, 168, 255))
    draw.ellipse([(32, 15), (42, 25)], fill=(249, 226, 175, 255))
    draw.ellipse([(50, 15), (60, 25)], fill=(166, 227, 161, 255))

    draw.text((75, 12), f"Postman - {request_name}", font=font_ui_bold, fill=(205, 214, 244, 255))

    # Request Bar (Method + URL + Status Pill)
    req_y = header_height + 10
    method_colors = {
        "GET": ((166, 227, 161, 255), (24, 50, 30, 255)),
        "POST": ((249, 226, 175, 255), (55, 45, 15, 255)),
        "PUT": ((137, 180, 250, 255), (20, 35, 60, 255)),
        "DELETE": ((243, 139, 168, 255), (60, 20, 30, 255)),
    }
    fg_col, bg_col = method_colors.get(method.upper(), ((205, 214, 244, 255), (40, 40, 50, 255)))

    # Method pill
    draw.rounded_rectangle([(padding, req_y), (padding + 70, req_y + 30)], radius=4, fill=bg_col, outline=fg_col, width=1)
    draw.text((padding + 16, req_y + 6), method.upper(), font=font_bold, fill=fg_col)

    # URL box
    url_box_left = padding + 80
    url_box_right = width - 160
    draw.rounded_rectangle([(url_box_left, req_y), (url_box_right, req_y + 30)], radius=4, fill=(30, 30, 46, 255), outline=(69, 71, 90, 255), width=1)
    draw.text((url_box_left + 12, req_y + 6), url, font=font, fill=(205, 214, 244, 255))

    # Status Pill
    status_str = str(status_code)
    is_success = status_str.startswith("2")
    status_bg = (24, 50, 30, 255) if is_success else (60, 20, 30, 255)
    status_fg = (166, 227, 161, 255) if is_success else (243, 139, 168, 255)
    status_box_left = width - 145
    status_box_right = width - padding
    draw.rounded_rectangle([(status_box_left, req_y), (status_box_right, req_y + 30)], radius=4, fill=status_bg, outline=status_fg, width=1)
    draw.text((status_box_left + 10, req_y + 6), f"Status: {status_str}", font=font_bold, fill=status_fg)

    # Response Header / Tabs
    resp_y = req_y + 42
    draw.line([(padding, resp_y), (width - padding, resp_y)], fill=(49, 50, 68, 255), width=1)
    draw.text((padding, resp_y + 6), "Response Body (JSON):", font=font_ui_bold, fill=(137, 220, 235, 255))

    # Draw body lines
    cur_y = resp_y + 30
    for bline in body_lines:
        # Simple JSON highlighting
        color = (205, 214, 244, 255)
        if ":" in bline:
            k, v = bline.split(":", 1)
            draw.text((padding, cur_y), k + ":", font=font, fill=(137, 180, 250, 255))
            draw.text((padding + len(k + ":") * 8 + 4, cur_y), v, font=font, fill=(166, 227, 161, 255) if any(x in v for x in ['"', 'true', 'false']) else (249, 226, 175, 255))
        else:
            draw.text((padding, cur_y), bline, font=font, fill=(203, 166, 247, 255))
        cur_y += line_height

    # Test Results section if any
    if test_lines:
        cur_y += 10
        draw.line([(padding, cur_y), (width - padding, cur_y)], fill=(49, 50, 68, 255), width=1)
        cur_y += 8
        draw.text((padding, cur_y), "Test Results:", font=font_ui_bold, fill=(166, 227, 161, 255))
        cur_y += 24
        for item in test_lines:
            if isinstance(item, (list, tuple)):
                msg, stat = item[0], item[1]
                tline = f"{stat}: {msg}"
            else:
                tline = str(item)
            t_col = (166, 227, 161, 255) if "PASS" in tline else (243, 139, 168, 255)
            symbol = "✓ " if "PASS" in tline else "✗ "
            draw.text((padding, cur_y), symbol + tline, font=font_bold, fill=t_col)
            cur_y += line_height

    filepath = os.path.join(SCREENSHOTS_DIR, filename)
    img.save(filepath, "PNG")
    return filepath

if __name__ == "__main__":
    render_postman_screenshot(
        "test_postman.png",
        "POST /api/auth/login",
        "POST",
        "http://localhost:9000/api/auth/login",
        200,
        {"accessToken": "eyJhbGciOiJIUzI1NiJ9...", "tokenType": "Bearer", "role": "ADMIN", "email": "admin@fucinema.com"},
        ["PASS: Status code is 200", "PASS: Response contains accessToken", "PASS: Role is ADMIN"]
    )
    print("Postman screenshot generated!")
