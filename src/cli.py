import click
import logging
from src.config import setup_logging
from src.config import VALID_ARCH, VALID_ENCRYPTION, VALID_FILE_SYSTEMS, VALID_INTERFACES
from src.core.configuration import Config
from src.core.resource_manager import ResourceManager
from src.core.builder import ConfigBuilder
from src.core.tester import ConfigTester
from src.core.parser import Parser


# setup log levels
setup_logging()
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

    # Adjust the log level after setting up logging
    if verbose:
        logger.info("LOG LEVEL: DEBUG")
        logger.setLevel(logging.DEBUG)
    else:
        logger.info("LOG LEVEL: INFO")

    if not configfile:
        configstring = f"{arch}-{filesystem}-{interface}-{encryption}"
    else:
        configstring = configfile

    # call parser to get list of Config Objects
    configs = Parser(configstring).generate_configs()
    logger.info(f"Parsed {len(configs)} configs.")

    # handles build only and test only logic
    if not build_only and not test_only:
        build_only = True
        test_only = True

    # lets build in series(some stuff is shared, need to fix it)
    successfull_builds = []
    if build_only:
        # since builder has copies of config in its class variables
        builders = [ ConfigBuilder(config) for config in configs ]
        for builder in builders:
            # logger.debug(f"Building Bootloader => {arch}-{filesystem}-{interface}-{encryption}")
            try:
                builder.build_resource()
                successfull_builds.append(builder.config)
                logger.debug("Build Successful")
            except Exception as e:
                logger.debug("Build Failed")
                logger.error(e)
            

    # test in parallel
    successfull_tests = []
    parallel_flag = True
    if test_only:
        configs_to_test = successfull_builds if build_only else configs
        testers = [ ConfigTester(config) for config in configs_to_test]
        if not parallel_flag:
            # sequence one by one
            for tester in testers:
                try:
                    status = tester.run_test()
                    if status :
                        successfull_tests.append(tester.config)
                        logger.debug("Test Passed")
                    else:
                        logger.debug("Test Failed")
                except Exception as e:
                    logger.debug("Test Failed")
                    logger.error(e)
        else:
            # submit to resource manager class (probably rename better)
            try:
                resource = ResourceManager(configs_to_test)
                resource.work()
            except Exception as e:
                logger.error(str(e))
                logger.error("Error Occurred while testing")
    

@main.command("setup")
@click.option("-v","--verbose", default="INFO", help="sets verbosity of output")
def setup(verbose):
    pass

if __name__ == "__main__":
    main()