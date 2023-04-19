def sanitize_size_chart_data(data):
    data = data["size_chart"]["0"]
    headers = data["header"]["0"]
    body = list(data["body"].values())

    result = []
    for size_data in body:
        item = {}
        for k, v in size_data.items():
            if k in headers:
                k = "size" if headers[k]["value"] == "" else k
                item[k] = v["value"]
        result.append(item)

    return result
