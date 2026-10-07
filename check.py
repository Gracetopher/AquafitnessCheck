BASE = "https://shop.baederportal-duisburg.de/de/bookings/block_list/bookable/0/tab/{tab}/sort_field/address_meta_name/sort_order/asc/?tab={tab}&items_per_page=100&page=1"
TABS = [3, 9]  # 3 = Aquafitnesskurse, 9 = Aquafitness Aktiv
KEYWORD = "Neudorf"
NTFY_TOPIC = os.environ["NTFY_TOPIC"]
SEEN = pathlib.Path("seen.json")

found = {}
for tab in TABS:
    html = requests.get(BASE.format(tab=tab), timeout=30,
                        headers={"User-Agent": "Mozilla/5.0"}).text
    soup = BeautifulSoup(html, "html.parser")
    for row in soup.select("tr"):
        link = row.select_one('a[href*="/course_blocks/details/"]')
        if not link:  # skips the header and the filter row
            continue
        cells = [c.get_text(" ", strip=True) for c in row.find_all("td")]
        if KEYWORD.lower() in " ".join(cells).lower():
            cid = link["href"].rstrip("/").split("/")[-1]
            found[cid] = " | ".join(cells)
for row in soup.select("tr"):
    link = row.select_one('a[href*="/course_blocks/details/"]')
    if not link:  # skips the header and the filter row
        continue
    cells = [c.get_text(" ", strip=True) for c in row.find_all("td")]
    if KEYWORD.lower() in " ".join(cells).lower():
        cid = link["href"].rstrip("/").split("/")[-1]
        found[cid] = " | ".join(cells)

seen = set(json.loads(SEEN.read_text())) if SEEN.exists() else set()
new = {k: v for k, v in found.items() if k not in seen}

for cid, desc in new.items():
    requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=desc.encode("utf-8"),
                  headers={"Title": "Neues Aquafitness-Angebot in Neudorf",
                           "Click": f"https://shop.baederportal-duisburg.de/de/course_blocks/details/{cid}/"})

SEEN.write_text(json.dumps(sorted(seen | set(found))))
