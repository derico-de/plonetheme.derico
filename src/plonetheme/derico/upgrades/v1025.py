"""Register the copper block background."""

BLICCA_PROFILE = "plone.blicca.auroraeditor:default"


def upgrade(context):
    """The record arrives with Blicca's upgrade 1006, which may still be pending."""
    context.upgradeProfile(BLICCA_PROFILE)
