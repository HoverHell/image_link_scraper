"""
Modules for obtaining listings of image-links from various sites.


Approximate iterfaces:

    site_specific_instance.get_items(...) -> [item_info, ...]

    item_info:
        url: ...,  # linked image / image(s) page
        id: ...,  # site-specific identifier.

"""
