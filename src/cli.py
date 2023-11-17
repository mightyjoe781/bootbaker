import click
import logging
from src.config import VALID_ARCH, VALID_ENCRYPTION, VALID_FILE_SYSTEMS, VALID_INTERFACES

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@click.group()
@click.version_option("0.1", prog_name="bootbaker")
def main():
    pass

@main.command("run")
@click.option("-c","--configfile", type=click.File(), help="Config file to run bootbaker")
@click.option("-s","--src", type=click.Path(exists=True, dir_okay=True, readable=True, executable=True), help="Config file to run bootbaker")
@click.option("-a","--arch", type=click.Choice(VALID_ARCH), default="*", help="architecture name")
@click.option("-i","--interface", type=click.Choice(VALID_INTERFACES), default="*", help="interface name")
@click.option("-f","--filesystem", type=click.Choice(VALID_FILE_SYSTEMS), help="filesystem name")
@click.option("-e","--encryption", type=click.Choice(VALID_ENCRYPTION), default=None, help="encryption strategy")
@click.option("-b","--build-only", default=False, help="Only builds bootloader")
@click.option("-t","--test-only", default=False, help="Only tests bootloader")
@click.option("-v","--verbose", default="INFO", help="sets verbosity of output")
def run(configfile, src, arch, interface, filesystem, encryption, build_only, test_only, verbose):
    click.echo("Hello you just pressed click!")

@main.command("setup")
@click.option("-v","--verbose", default="INFO", help="sets verbosity of output")
def setup(verbose):
    pass

if __name__ == "__main__":
    main()