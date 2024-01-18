from src.core.configuration import Config
import yaml
import itertools
from pathlib import Path



class Parser:
    arches = ["amd64:amd64", "i386:i386", "arm:armv7", "arm64:aarch64", "riscv:riscv64", "powerpc:powerpc64", "powerpc:powerpc64le"]
    filesystems = ["zfs", "ufs"]
    interfaces = ["gpt", "mbr"]
    encryptions = ["geli", "none"]
    blacklist_regexes = ["riscv:riscv64-*-mbr-*"]
    linuxboot_edk2_list = ["amd64:amd64-*-*-*","arm64:arm64-*-*-*"]

    def __init__(self, configfile: str):
        self.configfile = Path(configfile)

        if not self.configfile.is_file():
            raise FileNotFoundError(f"The specified config file '{configfile}' does not exist.")

        # Load the YAML file
        with open(configfile, 'r') as file:
            self.recipes = yaml.safe_load(file)
        print(self.recipes)


    def generate_regex_from_combination(self, combination):
        arch, fs, interface, encryption = combination
        return f"{arch}-{fs}-{interface}-{encryption}"

    def generate_combinations_from_regex(self, regex):
        arch, fs, interface, encryption = regex.split('-')
        params = [
            self.arches if arch == '*' else [arch],
            self.filesystems if fs == '*' else [fs],
            self.interfaces if interface == '*' else [interface],
            self.encryptions if encryption == '*' else [encryption]
        ]
        # returns list of tuple of (arch, fs, interface, encryption)
        combinations = list(itertools.product(*params))

        # map a function
        regex_list = list(map(lambda c : self.generate_regex_from_combination(c), combinations))
        return regex_list


    def generate_valid_combinations_from_regex(self, regex):

        # generate universe of combinations
        universe = self.generate_combinations_from_regex('*-*-*-*')

        blacklisted_combinations = []
        for blacklist_regex in self.blacklist_regexes:
            blacklisted_combinations.extend(self.generate_combinations_from_regex(blacklist_regex))

        # generate requested combination
        requested_combination = self.generate_combinations_from_regex(regex)

        # create valid combination
        universe_set = set(universe)
        blacklisted_set = set(blacklisted_combinations)
        valid_combination_set = universe_set - blacklisted_set

        valid_combination = [combo for combo in requested_combination if combo in valid_combination_set]

        return valid_combination

    def generate_configs(self):
        # create config from each recipe's config expression
        configs = []
        for _, recipe in self.recipes.items():
            combinations = []
            for regex in recipe['regex_combination']:
                regex_str = f"{recipe['arch']}-{regex}"
                combinations.extend(self.generate_combinations_from_regex(regex_str))
            port = 4000
            for combo in combinations:
                # each combo call config class to create config objects and put them in the configs array
                arch, fs, interface, encryption = combo.split('-')
                config = Config(
                    arch = arch,
                    filesystem = fs,
                    interface = interface,
                    flavor = recipe.get('flavor') or None,
                    img_file = recipe.get('img_file') or None,
                    img_url = recipe.get('img_url') or None,
                    port = port,
                    encryption = encryption,
                    version = recipe.get('version') or '13.2',
                    recipe = recipe
                )
                # increase port
                configs.append(config)
                port += 1
        return configs