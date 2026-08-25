"""Invoke tasks for plonetheme.derico."""
import shutil

from invoke import Exit
from invoke import task


@task
def install(c):
    """Install project dependencies."""
    c.run("uv sync")


@task
def start(c, instance="instance"):
    """Start a Plone instance."""
    c.run(f"uv run runwsgi var/{instance}/etc/zope.ini")


@task
def debug(c, instance="instance"):
    """Start a Plone instance in debug mode."""
    c.run(f"uv run runwsgi -d var/{instance}/etc/zope.ini")


@task
def shell(c, instance="instance"):
    """Open a Zope debug shell."""
    c.run(f"uv run zconsole debug var/{instance}/etc/zope.conf")


@task
def test(c, verbose=False):
    """Run tests."""
    cmd = "uv run --extra test pytest"
    if verbose:
        cmd += " -v"
    c.run(cmd)


@task
def create_instance(c, name="instance", port=8080):
    """Create a new Zope instance using the zope_instance template."""
    cmd = (
        f"copier copy --trust --defaults "
        f"--data instance_name={name} "
        f"--data port={port} "
    )
    cmd += "~/.copier-templates/plone-copier-templates/zope_instance ."
    c.run(cmd)


RECONFIGURE_TARGETS = {
    "addon": {
        "answers_file": ".copier-answers.yml",
        "template": "~/.copier-templates/plone-copier-templates/backend_addon",
    },
    "zope-setup": {
        "answers_file": ".copier-answers.zope-setup.yml",
        "template": "~/.copier-templates/plone-copier-templates/zope-setup",
    },
    "instance": {
        "answers_file": ".copier-answers.zope-instance-{name}.yml",
        "template": "~/.copier-templates/plone-copier-templates/zope_instance",
    },
}


@task
def reconfigure(c, target="instance", name="instance"):
    """Reconfigure a template target (re-asks all questions).

    Targets: addon, zope-setup, instance
    Use --name for instance targets (e.g. --name=instance2).
    """
    if target not in RECONFIGURE_TARGETS:
        print(f"Unknown target: {target}")
        print(f"Available targets: {', '.join(RECONFIGURE_TARGETS)}")
        return
    config = RECONFIGURE_TARGETS[target]
    answers_file = config["answers_file"].format(name=name)
    cmd = (
        f"copier recopy --trust --overwrite "
        f"-a {answers_file} "
        f"{config['template']} ."
    )
    c.run(cmd, pty=True)


@task
def create_site(c, site_id="Plone", instance="instance"):
    """Create a new Plone site."""
    import os
    import tempfile

    script = '''
from Testing.makerequest import makerequest
import transaction
app = makerequest(app)
from plone.distribution.api import site as site_api
site_api.create(
    app,
    "classic",
    {
        "site_id": "SITE_ID",
        "title": "Plonetheme Derico",
        "description": "A Plone addon package",
        "default_language": "en",
        "portal_timezone": "UTC",
        "setup_content": False,
    },
)
transaction.commit()
print("Created site: SITE_ID")
'''.replace("SITE_ID", site_id)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(script)
        script_path = f.name
    try:
        c.run(f"uv run zconsole run var/{instance}/etc/zope.conf {script_path}")
    finally:
        os.unlink(script_path)


@task
def build_blocks(c):
    """Build the brand blocks' editor bundles into static-blocks/.

    The artifacts are committed and nothing rebuilds them at install time, so
    run this after every change under bundle-src/src/ — CI runs
    `git diff --exit-code` over static-blocks/ and fails if you forget.
    """
    if not shutil.which("pnpm"):
        raise Exit(
            "pnpm is required to build the block bundles and was not found on "
            "PATH. Install it with `corepack enable`, or see bundle-src/README.md.",
            code=1,
        )
    c.run("pnpm --dir bundle-src install")
    c.run("pnpm --dir bundle-src build")


@task
def test_blocks(c):
    """Typecheck and unit-test the block bundles (vitest)."""
    if not shutil.which("pnpm"):
        raise Exit(
            "pnpm is required to test the block bundles and was not found on "
            "PATH. Install it with `corepack enable`, or see bundle-src/README.md.",
            code=1,
        )
    c.run("pnpm --dir bundle-src typecheck")
    c.run("pnpm --dir bundle-src test")


@task
def format(c):
    """Format code with ruff."""
    c.run("uv run ruff format .")
    c.run("uv run ruff check --fix .")


@task
def lint(c):
    """Run linting checks."""
    c.run("uv run ruff check .")
