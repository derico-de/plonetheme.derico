"""Install the Reference List block."""

from plone import api


PRODUCT = "collective.blicca.referencelist"


def upgrade(context):
    """GenericSetup applies a dependency profile on install only."""
    installer = api.addon.get_installer(api.portal.get())
    if not installer.is_product_installed(PRODUCT):
        installer.install_product(PRODUCT)
