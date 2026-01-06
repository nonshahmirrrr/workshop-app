from flask import session
from markupsafe import escape

NAV_ITEMS = [
    ("Customers", "/customers"),
    ("Vehicles", "/vehicles"),
    ("Mechanics", "/mechanics"),
    ("Services", "/services"),
    ("Parts", "/parts"),
    ("Records", "/records"),
    ("Bills", "/bills"),
]

# ✅ ORIGINAL DARK THEME + ANIMATIONS (same look, enhanced feel)
BASE_CSS = r"""
:root{
  --bg:#0b1220; --card:#121a2b; --card2:#0f1726;
  --text:#e8eefc; --muted:#a9b6d6; --line:#23304b;
  --accent:#4f7cff; --accent2:#2dd4bf; --danger:#ff5c7a;
  --shadow: 0 10px 30px rgba(0,0,0,.35);
  --radius: 14px;
  --font: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial;

  --ease: cubic-bezier(.2,.8,.2,1);
  --ease2: cubic-bezier(.16,1,.3,1);
}

*{box-sizing:border-box}
html,body{height:100%}

::selection{ background: rgba(79,124,255,.28); color: var(--text); }

body{
  margin:0; font-family:var(--font);
  background:
    radial-gradient(1200px 800px at 20% -10%, rgba(79,124,255,.25), transparent 60%),
    radial-gradient(900px 700px at 80% 0%, rgba(45,212,191,.18), transparent 55%),
    var(--bg);
  color:var(--text);

  /* animation-ready background */
  background-size: 150% 150%, 150% 150%, 100% 100%;
  animation: bgFloat 10s var(--ease2) infinite alternate;
}

/* subtle moving glow */
@keyframes bgFloat{
  0%   { background-position: 0% 0%,   100% 0%, 0% 0%; }
  100% { background-position: 10% 6%,  90% 12%, 0% 0%; }
}

a{color:var(--accent); text-decoration:none}
a:hover{text-decoration:underline}

.container{max-width:1100px; margin:0 auto; padding:22px 18px 44px}

/* page entrance animation */
.page{
  animation: pageIn .42s var(--ease2) both;
  transform-origin: top center;
}
@keyframes pageIn{
  from{ opacity:0; transform: translateY(8px) scale(.995); filter: blur(4px); }
  to  { opacity:1; transform: translateY(0) scale(1);     filter: blur(0); }
}

.topbar{
  position:sticky; top:0; z-index:10;
  background:rgba(11,18,32,.75); backdrop-filter: blur(10px);
  border-bottom:1px solid rgba(35,48,75,.7);
}
.topbar-inner{
  max-width:1100px; margin:0 auto; padding:14px 18px;
  display:flex; gap:14px; align-items:center; justify-content:space-between
}
.brand{
  display:flex; align-items:center; gap:10px; font-weight:800; letter-spacing:.2px;
  color:var(--text); text-decoration:none;
  position:relative;
}
.brand:hover{text-decoration:none; opacity:.95}

/* animated underline for brand */
.brand::after{
  content:"";
  position:absolute;
  left:0; bottom:-6px;
  height:3px; width:0%;
  border-radius:999px;
  background: linear-gradient(90deg, rgba(79,124,255,.9), rgba(45,212,191,.9));
  transition: width .25s var(--ease);
}
.brand:hover::after{ width: 100%; }

.badge{
  display:inline-block; padding:4px 10px;
  border:1px solid rgba(79,124,255,.45);
  color:var(--muted); border-radius:999px; font-size:12px
}

/* nav */
.nav{display:flex; gap:8px; flex-wrap:wrap}
.nav a{
  display:inline-flex;
  align-items:center;
  gap:8px;
  padding:8px 12px;
  border-radius:999px;
  border:1px solid rgba(35,48,75,.9);
  background:rgba(18,26,43,.45);
  color:var(--text);

  box-shadow:none;
  transform:translateY(0);
  position:relative;
  overflow:hidden;

  transition:
    transform .15s var(--ease),
    box-shadow .15s var(--ease),
    border-color .15s var(--ease),
    background .15s var(--ease),
    filter .15s var(--ease);
}

/* sheen animation */
.nav a::before{
  content:"";
  position:absolute;
  inset:-2px;
  background: linear-gradient(90deg,
    rgba(79,124,255,0),
    rgba(79,124,255,.25),
    rgba(45,212,191,.22),
    rgba(79,124,255,0)
  );
  transform: translateX(-120%);
  filter: blur(10px);
  opacity:0;
}
.nav a:hover::before{
  opacity:1;
  animation: sheen 1.05s var(--ease2) both;
}
@keyframes sheen{
  from{ transform: translateX(-120%); }
  to  { transform: translateX(120%); }
}

.nav a:hover{
  transform: translateY(-3px);
  box-shadow:
    0 0 0 1px rgba(79,124,255,.45),
    0 8px 20px rgba(79,124,255,.45);
  border-color: rgba(79,124,255,.9);
  background: rgba(79,124,255,.15);
  text-decoration:none;
}
.nav a:active{
  transform: translateY(1px) scale(.99);
  box-shadow:
    0 0 0 1px rgba(79,124,255,.35),
    0 4px 10px rgba(79,124,255,.35);
}
.nav a.active{
  border-color: rgba(79,124,255,.7);
  background: rgba(79,124,255,.12);
  box-shadow:none;
}

.header{
  display:flex; align-items:flex-end; justify-content:space-between; gap:14px;
  margin:18px 0 14px;
}
h1{margin:0; font-size:26px}
.sub{margin-top:6px; color:var(--muted); font-size:13px}

/* card hover lift */
.card{
  background:linear-gradient(180deg, rgba(18,26,43,.92), rgba(18,26,43,.7));
  border:1px solid rgba(35,48,75,.9);
  border-radius:var(--radius);
  box-shadow:var(--shadow);
  padding:16px;

  transform: translateY(0);
  transition: transform .18s var(--ease), box-shadow .18s var(--ease), border-color .18s var(--ease);
  position:relative;
  overflow:hidden;
}
.card::after{
  content:"";
  position:absolute;
  inset:-2px;
  background:
    radial-gradient(700px 140px at 20% 0%, rgba(79,124,255,.12), transparent 55%),
    radial-gradient(700px 140px at 80% 0%, rgba(45,212,191,.10), transparent 55%);
  opacity:0;
  transform: translateY(-10px);
  transition: opacity .25s var(--ease), transform .25s var(--ease);
  pointer-events:none;
}
.card:hover{
  transform: translateY(-2px);
  border-color: rgba(79,124,255,.35);
  box-shadow: 0 12px 34px rgba(0,0,0,.45);
}
.card:hover::after{
  opacity:1;
  transform: translateY(0);
}

.actions{display:flex; gap:10px; flex-wrap:wrap}

.btn{
  display:inline-flex;
  align-items:center;
  justify-content:center;
  gap:8px;
  padding:10px 12px;
  border-radius:12px;
  border:1px solid rgba(35,48,75,.9);
  background:rgba(15,23,38,.7);
  color:var(--text);
  cursor:pointer;

  transform: translateY(0);
  box-shadow:
    0 6px 0 rgba(0,0,0,.25),
    0 10px 20px rgba(0,0,0,.35);

  transition:
    transform .15s var(--ease),
    box-shadow .15s var(--ease),
    background .15s var(--ease),
    border-color .15s var(--ease),
    filter .15s var(--ease);
  position:relative;
  overflow:hidden;
}
.btn::before{
  content:"";
  position:absolute;
  inset:0;
  background: radial-gradient(220px 90px at 30% 0%, rgba(255,255,255,.14), transparent 60%);
  opacity:0;
  transition: opacity .15s var(--ease);
}
.btn:hover::before{ opacity: 1; }

.btn:hover{
  transform: translateY(-3px);
  box-shadow:
    0 10px 0 rgba(0,0,0,.22),
    0 18px 30px rgba(0,0,0,.45);
  border-color: rgba(79,124,255,.8);
  filter: saturate(1.05);
  text-decoration:none;
}
.btn:active{
  transform: translateY(2px) scale(.99);
  box-shadow:
    0 3px 0 rgba(0,0,0,.3),
    0 6px 10px rgba(0,0,0,.4);
}

.btn.primary{background:rgba(79,124,255,.22); border-color:rgba(79,124,255,.8)}
.btn.primary:hover{background:rgba(79,124,255,.3)}
.btn.ghost{background:transparent}
.btn.danger{background:rgba(255,92,122,.12); border-color:rgba(255,92,122,.5)}

.btn.primary{
  box-shadow:
    0 6px 0 rgba(25,60,160,.6),
    0 12px 24px rgba(79,124,255,.45);
}
.btn.primary:hover{
  box-shadow:
    0 10px 0 rgba(25,60,160,.6),
    0 20px 34px rgba(79,124,255,.6);
}

.grid{display:grid; grid-template-columns:1fr; gap:14px}

.table-wrap{overflow:auto; border-radius:12px; border:1px solid rgba(35,48,75,.85)}
table{width:100%; border-collapse:collapse; min-width:720px; background:rgba(15,23,38,.35)}
th,td{padding:10px 12px; border-bottom:1px solid rgba(35,48,75,.7); text-align:left; white-space:nowrap}
th{font-size:12px; color:var(--muted); font-weight:700; background:rgba(18,26,43,.55)}

/* animated row sweep on hover */
tbody tr{ position:relative; }
tbody tr::after{
  content:"";
  position:absolute;
  left:-30%;
  top:0; bottom:0;
  width:30%;
  background: linear-gradient(90deg, transparent, rgba(79,124,255,.12), transparent);
  opacity:0;
  transform: translateX(-80%);
  pointer-events:none;
}
tr:hover td{background:rgba(79,124,255,.06)}
tbody tr:hover::after{
  opacity:1;
  animation: rowSweep .9s var(--ease2) both;
}
@keyframes rowSweep{
  from{ transform: translateX(-80%); }
  to  { transform: translateX(380%); }
}

form{display:grid; gap:12px}
.field{display:grid; gap:6px}
label{font-size:12px; color:var(--muted)}
input, select{
  padding:10px 12px; border-radius:12px;
  border:1px solid rgba(35,48,75,.9);
  background:rgba(15,23,38,.6);
  color:var(--text); outline:none;
  transition: box-shadow .18s var(--ease), border-color .18s var(--ease), transform .18s var(--ease);
}
input:focus, select:focus{
  border-color:rgba(79,124,255,.85);
  box-shadow:0 0 0 3px rgba(79,124,255,.15);
  transform: translateY(-1px);
}
.footer-note{margin-top:10px; color:var(--muted); font-size:12px}

/* Dashboard big icon cards */
.dash{
  display:grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap:14px;
}
.dashcard{
  display:block;
  padding:18px;
  border-radius:var(--radius);
  border:1px solid rgba(35,48,75,.9);
  background:linear-gradient(180deg, rgba(18,26,43,.92), rgba(18,26,43,.65));
  box-shadow:var(--shadow);
  text-decoration:none;
  color:var(--text);
  transform: translateY(0);
  position:relative;
  overflow:hidden;
  transition: transform .15s var(--ease), box-shadow .15s var(--ease), border-color .15s var(--ease), filter .15s var(--ease);
}
.dashcard::before{
  content:"";
  position:absolute;
  inset:-2px;
  background: linear-gradient(90deg,
    rgba(79,124,255,0),
    rgba(79,124,255,.22),
    rgba(45,212,191,.18),
    rgba(79,124,255,0)
  );
  transform: translateX(-120%);
  filter: blur(12px);
  opacity:0;
  pointer-events:none;
}
.dashcard:hover{
  transform: translateY(-4px);
  border-color: rgba(79,124,255,.9);
  box-shadow: 0 0 0 1px rgba(79,124,255,.35), 0 18px 35px rgba(0,0,0,.45);
  text-decoration:none;
  filter: saturate(1.06);
}
.dashcard:hover::before{
  opacity:1;
  animation: sheen 1.05s var(--ease2) both;
}
.dashcard .ico{font-size:34px; line-height:1;}
.dashcard .ttl{margin-top:10px; font-weight:900; font-size:16px;}
.dashcard .sub2{margin-top:6px; color:var(--muted); font-size:12px;}

/* focus accessibility */
:focus-visible{
  outline: 3px solid rgba(45,212,191,.35);
  outline-offset: 2px;
  border-radius: 10px;
}

/* reduced motion */
@media (prefers-reduced-motion: reduce){
  *{ animation-duration: 0.001ms !important; animation-iteration-count: 1 !important; transition-duration: 0.001ms !important; }
  body{ animation:none !important; }
}
"""


def render_page(title: str, active_path: str, body_html: str, subtitle: str = ""):
    nav_links = []
    for name, path in NAV_ITEMS:
        cls = "active" if path == active_path else ""
        nav_links.append(f'<a class="{cls}" href="{path}">{escape(name)}</a>')
    nav_html = "".join(nav_links)

    nav_block = f"<div class='nav'>{nav_html}</div>" if session.get("logged_in") else ""

    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>{BASE_CSS}</style>
</head>
<body>
  <div class="topbar">
    <div class="topbar-inner">
      <a class="brand" href="/dashboard">🔧 Workshop Manager</a>
      {nav_block}
    </div>
  </div>

  <div class="container page">
    <div class="header">
      <div>
        <h1>{escape(title)}</h1>
        <div class="sub">{escape(subtitle) if subtitle else ""}</div>
      </div>
    </div>

    <div class="grid">
      {body_html}
    </div>
  </div>
</body>
</html>
"""


def table(headers, rows, row_html_fn):
    thead = "".join([f"<th>{escape(h)}</th>" for h in headers])
    tbody = "".join([row_html_fn(r) for r in rows])
    return f"""
    <div class="card">
      <div class="table-wrap">
        <table>
          <thead><tr>{thead}</tr></thead>
          <tbody>{tbody}</tbody>
        </table>
      </div>
    </div>
    """
