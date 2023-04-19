import json

from services.models import CoordinatedProduct, ProductInformation, ProductReview, ProductTechnology


def process_single_product(product):
    processed_data = {
        "product_id": product["product_stat"]["article"],
        "product_name": product["product_data"]["name"],
        "product_url": product["product_data"]["url"],
        "product_category": product["product_data"]["category"],
        "available_sizes": product["product_data"]["available_sizes"],
        "breadcrumb": product["product_data"]["breadcrumb"],
        "sense_of_fit": product["product_data"]["sense_of_fit"],
        "title_of_description": product["product_data"]["title_of_description"],
        "product_description": product["api_info"]["product"]["article"]["description"]["messages"]["mainText"],
        "itemization_description": product["product_data"]["itemization_description"],
        "keywords": product["api_info"]["page"]["categories"],
    }

    if product["review_data"]:
        processed_data["product_rating"] = product["review_data"]["rating"]
        processed_data["number_of_reviews"] = product["review_data"]["number_of_reviews"]
        processed_data["recommended_rate"] = product["review_data"]["recommended_rate"]
        processed_data["sense_of_fit_rate"] = product["review_data"]["sense_of_fit_rate"]
        processed_data["appropriation_of_length_rate"] = product["review_data"]["appropriation_of_length_rate"]
        processed_data["material_quality_rate"] = product["review_data"]["material_quality_rate"]
        processed_data["comfort_rate"] = product["review_data"]["comfort_rate"]

    processed_data = ProductInformation(**processed_data)
    return processed_data.dict()


def prepare_products(data):
    processed_data = []
    for product in data:
        processed_data.append(process_single_product(product))

    with open("processed_data.json", "w", encoding="utf-8") as writer:
        writer.write(json.dumps(processed_data, indent=4, ensure_ascii=False))


def process_product_coordinates(product):
    result = []
    for coordinated_product in product["api_info"]["product"]["article"]["coordinates"]["articles"]:
        result.append(
            CoordinatedProduct(
                main_product_id=product["product_stat"]["article"],
                main_product_name=product["product_data"]["name"],
                coordinated_product_number=coordinated_product["articleCode"],
                coordinated_product_name=coordinated_product["name"],
                coordinated_product_price=coordinated_product["price"]["current"]["withTax"],
                coordinated_product_page_url=coordinated_product["articleCode"],
                coordinated_product_image_url=coordinated_product["image"],
            ).dict(),
        )
    return result


def prepare_product_coordinates(products):
    processed_data = []
    for product in products:
        if product["api_info"]["product"]["article"]["coordinates"]:
            processed_data.extend(process_product_coordinates(product))

    with open("processed_product_coordinates.json", "w", encoding="utf-8") as writer:
        writer.write(json.dumps(processed_data, indent=4, ensure_ascii=False))


def process_product_sizes(product):
    product_choices = []
    sizes = product["size_chart"]
    for size in sizes:
        product_choices.append(
            {
                "product_id": product["product_stat"]["article"],
                "product_name": product["product_data"]["name"],
                **size,
            }
        )
    return product_choices


def prepare_product_sizes(products):
    processed_data = []
    for product in products:
        size_data = process_product_sizes(product)
        if not size_data:
            continue
        processed_data.extend(size_data)

    with open("processed_size.json", "w", encoding="utf-8") as writer:
        writer.write(json.dumps(processed_data, indent=4, ensure_ascii=False))


def process_product_technologies(product):
    result = []
    for tech in product["api_info"]["product"]["model"]["description"]["technology"]:
        result.append(
            ProductTechnology(
                product_id=product["product_stat"]["article"],
                product_name=product["product_data"]["name"],
                technology_name=tech["name"],
                description=tech["text"],
                image_url=tech["imagePath"],
            ).dict(),
        )
    return result


def process_special_functions(products):
    processed_data = []
    for product in products:
        if product["api_info"]["product"]["model"]["description"]["technology"]:
            processed_data.extend(process_product_technologies(product))

    with open("processed_technologies.json", "w", encoding="utf-8") as writer:
        writer.write(json.dumps(processed_data, indent=4, ensure_ascii=False))


def process_product_reviews(product):
    product_reviews = []
    for review in product["review_data"]["reviews"]:
        product_reviews.append(
            ProductReview(
                product_id=product["product_stat"]["article"],
                product_name=product["product_data"]["name"],
                **review,
            ).dict(),
        )
    return product_reviews


def prepare_product_reviews(products):
    processed_data = []
    for product in products:
        if product["review_data"]:
            processed_data.extend(process_product_reviews(product))

    with open("processed_reviews.json", "w", encoding="utf-8") as writer:
        writer.write(json.dumps(processed_data, indent=4, ensure_ascii=False))