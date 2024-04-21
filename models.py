import hashlib
from datetime import datetime, timedelta
from pathlib import Path
import json
from dateutil.parser import parse
from dateutil.tz import UTC, tzlocal
import boto3
from configparser import ConfigParser
from datetime import datetime, timezone

AWS_SSO_CACHE_PATH = f'{Path.home()}/.aws/sso/cache'
AWS_CREDENTIAL_PATH = f'{Path.home()}/.aws/credentials'

class AWSProfile:

    def __read_config(self, path: str):
        config = ConfigParser()
        config.read(path)
        return config

    def __write_config(self, path, config):
        with open(path, "w") as destination:
            config.write(destination)
    def __init__(self, name: str, region: str, account_id: str, role_name: str, session: str):
        self.name = name
        self.region = region
        self.account_id = account_id
        self.role_name = role_name
        self.session = session
        self.expires_in = self.__calculate_time_to_expiry()
        self.sso_cache_expiration = self.__calculate_sso_cache_expiration()

    def _load_json(self,path):
        try:
            with open(path) as context:
                return json.load(context)
        except ValueError:
            return {}

    def get_new_credentials(self):
        login = self.__get_sso_cached_login()
        if login == 'Expired':
            return None
        client = boto3.client('sso', region_name=self.region)
        response = client.get_role_credentials(
            roleName=self.role_name,
            accountId=self.account_id,
            accessToken=login['accessToken'],
        )
        return response["roleCredentials"]

    def __get_sso_cached_login(self):
        cache = hashlib.sha1(self.session.encode("utf-8")).hexdigest()
        sso_cache_file = f'{AWS_SSO_CACHE_PATH}/{cache}.json'

        if not Path(sso_cache_file).is_file():
            return {'Error' : 'Error'}
        else:
            data = self._load_json(sso_cache_file)
            now = datetime.now().astimezone(UTC)
            expires_at = parse(data['expiresAt']).astimezone(UTC)
            if now > expires_at:
                return 'Expired'
            if (now + timedelta(minutes=15)) >= expires_at:
               pass

        return data

    def __calculate_time_to_expiry(self):
        config = self.__read_config(AWS_CREDENTIAL_PATH)

        try:
            profile_item = config.__getitem__(self.name)
        except:
            return 'Expiry not found'
        if profile_item == None:
            return 'Expiry not found'
        expiry_stamp =  profile_item.get('expires',None)
        if expiry_stamp == None:
            return 'Expiry not found'
            # Convert timestamp to milliseconds
        timestamp_in_ms = int(expiry_stamp)

        # Convert milliseconds to datetime object in UTC
        timestamp_dt = datetime.fromtimestamp(timestamp_in_ms / 1000.0, tz=timezone.utc)

        # Get current time in UTC
        current_time_utc = datetime.now(timezone.utc)

        # Calculate the difference in minutes
        delta = timestamp_dt - current_time_utc
        difference_in_minutes = int(delta.total_seconds() / 60)

        return self.__minutes_to_message(difference_in_minutes)

    def __minutes_to_message(self,difference_in_minutes : int):
        if difference_in_minutes < 0:
            return 'Expired'
        elif difference_in_minutes < 60:
            return f'{int(difference_in_minutes)} minutes'
        else:
            return f'{int(difference_in_minutes/60)} hours {int(difference_in_minutes%60)} minutes'

    def __calculate_sso_cache_expiration(self):
        cache = hashlib.sha1(self.session.encode("utf-8")).hexdigest()
        sso_cache_file = f'{AWS_SSO_CACHE_PATH}/{cache}.json'

        if not Path(sso_cache_file).is_file():
            return {'Error': 'Error'}
        else:
            data = self._load_json(sso_cache_file)
            expires_at = parse(data['expiresAt']).astimezone(UTC)
            now = datetime.now().astimezone(UTC)
            timedelta = expires_at - now
            minutes = int(timedelta.total_seconds() / 60)
            return self.__minutes_to_message(minutes)
        pass

