from requests import Session

QUERY_URL = "https://reware-production.yerdle.io/v4/graphql"

ITEM_URL_TEMPLATE = "https://wornwear.patagonia.com/shop/{slug}/{parentSKU}/{color}"


def fetch_titles(session, offset, limit):
    query = """
    {
        partner(uuid: "7d32ad83-330e-4ccc-ba03-3bb32ac113ac") {
            categories {
                slug
                inventoryItemsForSale(
                    facets: [{ tag:"size" name:"S" }]
    """ + """
        limit: {limit}
        offset: {offset}
    """.format(offset=offset, limit=limit) + """
                    sort: "pr"
                ) {
                    title
                    color
                    parentSKU
                    price
                }
            }
        }
    }
    """

    resp = session.post(QUERY_URL, json=dict(query=query))
    cats = resp.json()['data']['partner']['categories']
    for cat in cats:
        slug = cat['slug']
        items = cat['inventoryItemsForSale']
        for i in items:
            i['slug'] = slug
            yield i


def titles():
    session = Session()
    offset = 0
    limit = 50
    while True:
        titles = list(fetch_titles(session, offset=offset, limit=limit))
        if not titles:
            break
        offset += limit
        for t in titles:
            yield t


def main(*argv):
    for t in titles():
        t['price'] = int(t['price'] / 100)
        t['url'] = ITEM_URL_TEMPLATE.format(**t)
        print('{title}: ${price} {url}'.format(**t))


if __name__ == '__main__':
    from sys import argv
    main(*argv)
