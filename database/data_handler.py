

def format_data(raw_data, key_order):
    # Rebuild the return as a dict of dicts with display order for render
    data = {}
    for item in raw_data:
        data.update({str(item["id"]): {}})

        for key in key_order:
            data[str(item["id"])].update({key: str(item[key])})

    return data
