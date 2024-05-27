from ir_datasets import main_cli as irds_main_cli
from ir_datasets_webis.webis_mastodon_2024 import register as register_webis_mastodon_2024


def register() -> None:
    register_webis_mastodon_2024()


def main_cli() -> None:
    register()
    irds_main_cli()
