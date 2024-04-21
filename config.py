from configparser import ConfigParser
from pathlib import Path
import subprocess
from typing import List
import multiprocessing
from models import AWSProfile
import sys
import re
AWS_CONFIG_PATH = f'{Path.home()}/.aws/config'
AWS_CREDENTIAL_PATH = f'{Path.home()}/.aws/credentials'
AWS_SSO_CACHE_PATH = f'{Path.home()}/.aws/sso/cache'
AWS_DEFAULT_REGION = 'eu-west-1'


class ConfigFile:

    def __create_aws_profile_from_config(self, config: ConfigParser, name: str):
        item = config.__getitem__(name)
        aws_profile = AWSProfile(region=item.__getitem__('region') if item.keys().__contains__('region') else "no-region-available",
                                 account_id=item.__getitem__('sso_account_id'),
                                 role_name=item.__getitem__('sso_role_name'),
                                 session=item.__getitem__('sso_session'),
                                 name=item.name
                                 )
        return aws_profile

    def store_aws_credentials(self,awsprofile : AWSProfile, credentials):

        region = awsprofile.region
        config = self.__read_config(AWS_CREDENTIAL_PATH)

        if config.has_section(awsprofile.name):
            config.remove_section(awsprofile.name)

        config.add_section(awsprofile.name)
        config.set(awsprofile.name, "region", region)
        config.set(awsprofile.name, "aws_access_key_id", credentials["accessKeyId"])
        config.set(awsprofile.name, "aws_secret_access_key ", credentials["secretAccessKey"])
        config.set(awsprofile.name, "aws_session_token", credentials["sessionToken"])
        config.set(awsprofile.name, "expires",str(credentials["expiration"]))
        self.__write_config(AWS_CREDENTIAL_PATH, config)

    def getProfiles(self) -> List[AWSProfile]:
        config = self.__read_config(AWS_CONFIG_PATH)
        profile_sections = list(filter(lambda x: str(x).startswith('profile'), config.sections()))
        aws_profiles = list(map(lambda x: self.__create_aws_profile_from_config(config, x), profile_sections))
        return aws_profiles

    def __read_config(self, path: str):
        config = ConfigParser()
        config.read(path)
        return config

    def __write_config(self, path, config):
        with open(path, "w") as destination:
            config.write(destination)

    def move_profile_to_default(self, aws_profile: AWSProfile):
        config = self.__read_config(AWS_CONFIG_PATH)
        if config.has_section('default'):
            config.remove_section('default')

        config.add_section('default')
        for key, value in config.items(aws_profile.name):
            config.set('default', key, value)

        self.__write_config(AWS_CONFIG_PATH, config)

        config = self.__read_config(AWS_CREDENTIAL_PATH)
        if config.has_section('default'):
            config.remove_section('default')
        config.add_section('default')
        for key, value in config.items(aws_profile.name):
            config.set('default', key, value)
        self.__write_config(AWS_CREDENTIAL_PATH, config)
        return ''

    def spawn_cli_for_auth(self,profile : str):
        cmd = ['aws']
        subprocess.run(cmd + ['sso', 'login', '--profile', re.sub(r"^profile ", "", str(profile))],
                       stderr=sys.stderr,
                       stdout=sys.stdout,
                       check=True)
    def spawn_cli_for_auth2(self,profile : str):
        subprocess.Popen(['aws' , 'sso', 'login', '--profile', re.sub(r"^profile ", "", str(profile))])
    def get_profile_by_name(self,profile_name :str) -> AWSProfile:
        print(profile_name)
        profiles = [profile for profile in self.getProfiles() if profile.name == profile_name]
        return profiles[0]
