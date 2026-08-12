"""Testing setup for plonetheme.derico."""
import os

import plone.app.theming
import plone.pageletlayout
import plone.restapi
import plonetheme.clara
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.testing.zope import WSGI_SERVER_FIXTURE

import plonetheme.derico


class PlonethemeDericoLayer(PloneSandboxLayer):
    """Custom testing layer for plonetheme.derico."""

    def setUpZope(self, app, configurationContext):
        """Set up Zope."""
        # Compile .po -> .mo so add-on translations load during tests.
        os.environ.setdefault("zope_i18n_compile_mo_files", "true")
        self.loadZCML(package=plone.app.theming)
        self.loadZCML(package=plone.restapi)
        # derico is a token layer on Clara, which is itself a theme on
        # plone.pageletlayout. z3c.autoinclude wires this up in a real
        # instance; the sandbox layer has to load the chain by hand so
        # profile-plonetheme.clara:default exists when derico's
        # dependency-profile install asks for it.
        self.loadZCML(package=plone.pageletlayout)
        self.loadZCML(package=plonetheme.clara)
        self.loadZCML(package=plonetheme.derico)

    def setUpPloneSite(self, portal):
        """Set up Plone site."""
        self.applyProfile(portal, "plonetheme.derico:default")


FIXTURE = PlonethemeDericoLayer()

INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,),
    name="PlonethemeDericoLayer:IntegrationTesting",
)

FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,),
    name="PlonethemeDericoLayer:FunctionalTesting",
)

ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(FIXTURE, WSGI_SERVER_FIXTURE),
    name="PlonethemeDericoLayer:AcceptanceTesting",
)


# Test credentials
TEST_USER_ID = "testuser"
TEST_USER_NAME = "testuser"
SITE_OWNER_NAME = SITE_OWNER_NAME
SITE_OWNER_PASSWORD = SITE_OWNER_PASSWORD
