from LibDemNews.items import BlogItem


def test_blog_item():
    item = BlogItem(content="")

    assert item["content"] == ""
