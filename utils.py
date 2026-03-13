def deduplicate(resources):
    seen = set()
    unique = []
    for r in resources:
        key = (r["skill"].lower(), r["url"])
        if key not in seen:
            unique.append(r)
            seen.add(key)
    return unique