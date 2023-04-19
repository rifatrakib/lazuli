def sanitize_size_chart_data(data):
    data = data["size_chart"]["0"]
    headers = data["header"]["0"]
    body = list(data["body"].values())

    result = []
    for size_data in body:
        item = {}
        for k, v in size_data.items():
            if k in headers:
                if headers[k]["value"] == "":
                    item["表示サイズ"] = v["value"]
                else:
                    item[headers[k]["value"]] = v["value"].replace("cm", "")
        result.append(item)

    return result
