import click
import logging
from src.config import VALID_ARCH, VALID_ENCRYPTION, VALID_FILE_SYSTEMS, VALID_INTERFACES
from src.core.configuration import Config
from src.core.builder import ConfigBuilder
from src.core.tester import ConfigTester

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@click.group()
@click.version_option("0.1", prog_name="bootbaker")
def main():
    """
Example(s):\n
    bootbaker run -a amd64:amd64 -i gpt -f ufs -e none -v -b\n
    """
    pass

@main.command("run")
@click.option("-c","--configfile", type=click.File(), help="Config file to run bootbaker")
@click.option("-s","--src", type=click.Path(exists=True, dir_okay=True, readable=True, executable=True), help="path to freebsd source tree")
@click.option("-a","--arch", type=click.Choice(VALID_ARCH), default="*", help="architecture name")
@click.option("-i","--interface", type=click.Choice(VALID_INTERFACES), default="*", help="interface name")
@click.option("-f","--filesystem", type=click.Choice(VALID_FILE_SYSTEMS), help="filesystem name")
@click.option("-e","--encryption", type=click.Choice(VALID_ENCRYPTION), default=None, help="encryption strategy")
@click.option("-b","--build-only", default=False, help="Only builds bootloader", is_flag=True)
@click.option("-t","--test-only", default=False, help="Only tests bootloader", is_flag=True)
@click.option("-v","--verbose", default=False, help="sets verbosity of output", is_flag=True)
def run(configfile, src, arch, interface, filesystem, encryption, build_only, test_only, verbose):

    if verbose:
        logger.setLevel(logging.DEBUG)

    # handles build only and test only logic
    if not build_only and not test_only:
        build_only = True
        test_only = True

    port = 4000
    # TODO: A parser should parse configfile and generate list of config based on some rule
    # Port should be dynamically generated
    
    try:
        config = Config(arch, filesystem, interface, None, None, None, port, encryption)
        if build_only:
            logger.debug(f"Building Bootloader => {arch}-{filesystem}-{interface}-{encryption}")
            builder = ConfigBuilder(config)
            builder.build_resource()
            logger.debug("Build Successful")
        if test_only:
            logger.debug(f"Testing Bootloader => {arch}-{filesystem}-{interface}-{encryption}")
            tester = ConfigTester(config)
            # tester.run_script()
            logger.debug("Test Successful")
    except Exception as e:
        logger.error(e)

@main.command("setup")
@click.option("-v","--verbose", default="INFO", help="sets verbosity of output")
def setup(verbose):
    pass

if __name__ == "__main__":
    main()