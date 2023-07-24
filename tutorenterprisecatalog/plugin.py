from __future__ import annotations

from glob import glob
import os
import pkg_resources
from tutor import hooks as tutor_hooks

from .__about__ import __version__

from tutor import hooks as tutor_hooks

templates = pkg_resources.resource_filename("tutorenterprisecatalog", "templates")

# Add the "templates" folder as a template root
tutor_hooks.Filters.ENV_TEMPLATE_ROOTS.add_item(
    pkg_resources.resource_filename("tutorenterprisecatalog", "templates")
)

config = {
    "add": {
        "MYSQL_PASSWORD": "{{ 8|random_string }}",
        "SECRET_KEY": "{{ 24|random_string }}",
        "OAUTH2_SECRET": "{{ 8|random_string }}",
        "OAUTH2_SECRET_SSO": "{{ 8|random_string }}",
    },
    "defaults": {
        "VERSION": __version__,
        "DOCKER_IMAGE": "{{ DOCKER_REGISTRY }}diceytech/openedx-enterprise-catalog:{{ ENTERPRISECATALOG_VERSION }}",
        "WORKER_DOCKER_IMAGE": "openedx-enterprise-catalog-worker",
        "HOST": "enterprisecatalog.{{ LMS_HOST }}",
        "MYSQL_DATABASE": "enterprisecatalog",
        "MYSQL_USERNAME": "enterprisecatalog",
        "OAUTH2_KEY": "enterprisecatalog",
        "OAUTH2_KEY_DEV": "enterprisecatalog-dev",
        "OAUTH2_KEY_SSO": "enterprisecatalog-sso",
        "OAUTH2_KEY_SSO_DEV": "enterprisecatalog-sso-dev",
        "CACHE_REDIS_DB": "{{ OPENEDX_CACHE_REDIS_DB }}",
    },
}

tutor_hooks.Filters.IMAGES_BUILD.add_items(
    [
        (
            "enterprisecatalog",
            ("plugins", "enterprisecatalog", "build", "enterprisecatalog"),
            "{{ ENTERPRISECATALOG_DOCKER_IMAGE }}",
            (),
        ),
    ]
)


MY_INIT_TASKS: list[tuple[str, tuple[str, ...]]] = [
    ("mysql", ("enterprisecatalog", "hooks", "mysql", "init")),
    ("lms", ("enterprisecatalog", "hooks", "lms", "init")),
    ("enterprisecatalog", ("enterprisecatalog", "hooks", "enterprisecatalog", "init")),
]


for service, template_path in MY_INIT_TASKS:
    full_path: str = pkg_resources.resource_filename(
        "tutorenterprisecatalog", os.path.join("templates", *template_path)
    )
    with open(full_path, encoding="utf-8") as init_task_file:
        init_task: str = init_task_file.read()
    tutor_hooks.Filters.CLI_DO_INIT_TASKS.add_item((service, init_task))


def patches():
    all_patches = {}
    patches_dir = pkg_resources.resource_filename("tutorenterprisecatalog", "patches")
    for path in glob(os.path.join(patches_dir, "*")):
        with open(path) as patch_file:
            name = os.path.basename(path)
            content = patch_file.read()
            all_patches[name] = content
    return all_patches
