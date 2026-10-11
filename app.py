from html import escape
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs


users = {}
next_user_id = 1


class UserApp(BaseHTTPRequestHandler):
    def do_GET(self):
        rows = "".join(
            "<tr>"
            f"<td>{user_id}</td>"
            f"<td>{escape(user['name'])}</td>"
            f"<td>{escape(user['email'])}</td>"
            f"<td>{escape(user['age']) or '—'}</td>"
            "</tr>"
            for user_id, user in users.items()
        )
        if not rows:
            rows = '<tr><td colspan="4" class="empty">No users yet</td></tr>'

        page = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>User directory</title>
  <style>
    :root {{ color-scheme: light; font-family: Georgia, 'Times New Roman', serif; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: #f3f2ec; color: #202720; }}
    header {{ padding: 24px max(24px, calc((100% - 960px) / 2)); background: #244b3c; color: #fff; }}
    header span {{ font: 12px Arial, sans-serif; letter-spacing: 1px; text-transform: uppercase; color: #c6dfbf; }}
    h1 {{ margin: 8px 0 0; font-size: 32px; font-weight: 500; }}
    main {{ max-width: 960px; margin: 36px auto; padding: 0 24px; display: grid; grid-template-columns: 280px 1fr; gap: 48px; }}
    h2 {{ margin: 0 0 18px; font-size: 21px; font-weight: 500; }}
    label {{ display: block; margin: 14px 0 6px; font: 13px Arial, sans-serif; color: #425046; }}
    input {{ width: 100%; padding: 11px 12px; border: 1px solid #b8c0b7; border-radius: 3px; background: #fff; font: 15px Arial, sans-serif; }}
    button {{ margin-top: 18px; padding: 11px 16px; border: 0; border-radius: 3px; background: #c45435; color: #fff; font: 14px Arial, sans-serif; cursor: pointer; }}
    button:hover {{ background: #a9432b; }}
    .count {{ margin: -8px 0 14px; font: 13px Arial, sans-serif; color: #68736a; }}
    table {{ width: 100%; border-collapse: collapse; text-align: left; font: 14px Arial, sans-serif; }}
    th, td {{ padding: 12px 10px; border-bottom: 1px solid #d5d8d0; }}
    th {{ color: #526056; font-size: 12px; font-weight: 600; text-transform: uppercase; }}
    .empty {{ padding: 24px 10px; color: #758077; text-align: center; }}
    @media (max-width: 640px) {{ main {{ grid-template-columns: 1fr; gap: 34px; margin: 28px auto; }} section {{ min-width: 0; overflow-x: auto; }} table {{ min-width: 440px; }} }}
  </style>
</head>
<body>
  <header><span>Local app · in-memory storage</span><h1>User directory</h1></header>
  <main>
    <section>
      <h2>Add a user</h2>
      <form method="post" action="/users">
        <label for="name">Name</label>
        <input id="name" name="name" autocomplete="name" required maxlength="100">
        <label for="email">Email</label>
        <input id="email" name="email" type="email" autocomplete="email" required maxlength="254">
        <label for="age">Age</label>
        <input id="age" name="age" type="number" min="0" max="150">
        <button type="submit">Add user</button>
      </form>
    </section>
    <section>
      <h2>Saved users</h2>
      <p class="count">{len(users)} {"user" if len(users) == 1 else "users"}</p>
      <table>
        <thead><tr><th>ID</th><th>Name</th><th>Email</th><th>Age</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </section>
  </main>
</body>
</html>"""
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(page.encode("utf-8"))

    def do_POST(self):
        global next_user_id
        if self.path != "/users":
            self.send_error(404)
            return

        length = int(self.headers.get("Content-Length", "0"))
        fields = parse_qs(self.rfile.read(length).decode("utf-8"))
        name = fields.get("name", [""])[0].strip()
        email = fields.get("email", [""])[0].strip()
        age = fields.get("age", [""])[0].strip()
        if not name or not email or (age and not age.isdigit()):
            self.send_error(400, "Please provide a name, valid email, and numeric age.")
            return

        users[next_user_id] = {"name": name, "email": email, "age": age}
        next_user_id += 1
        self.send_response(303)
        self.send_header("Location", "/")
        self.end_headers()


if __name__ == "__main__":
    print("Serving user directory at http://127.0.0.1:8000")
    HTTPServer(("127.0.0.1", 8000), UserApp).serve_forever()