def sanitize_size_chart_data(data):
    data = data["size_chart"]["0"]
    headers = data["header"]["0"]
    body = list(data["body"].values())

    result = []
    for size_data in body:
        item = {headers[k]["value"]: v["value"] for k, v in headers.items()}
        for k, v in size_data.items():
            k = "size" if k == "" else k
            if k in headers:
                item[headers[k]["value"]] = v["value"]
        result.append(item)

    return result
