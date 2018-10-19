import sys
import abc
from abc import abstractmethod

import json
import mimetypes
import os
import subprocess
from uuid import uuid4

import yaml

import boto3
# from pynamodb.attributes import BooleanAttribute, UnicodeAttribute, MapAttribute, UTCDateTimeAttribute, NumberAttribute
# from pynamodb.models import Model


class Component(abc.ABC):

    @abstractmethod
    def init(self, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def update(self, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def status(self, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def teardown(self, **kwargs):
        raise NotImplementedError()


class WebComponent(Component):

    def __init__(self, **kwargs):
        self.client = boto3.client('s3')
        self.bucket_name = kwargs['stack_name']
        self.directory = kwargs.get('directory')

        self.website_configuration = {
            'ErrorDocument': {'Key': 'index.html'},
            'IndexDocument': {'Suffix': 'index.html'},
        }

    def init(self, **kwargs):
        # create the bucket
        self.bucket = self.client.create_bucket(
            Bucket=self.bucket_name + "-fup",
            ACL='public-read'
        )
        self.client.put_bucket_website(
            Bucket=self.bucket_name + "-fup",
            WebsiteConfiguration=self.website_configuration
        )
        self.update()
        return self.bucket_name + "-fup"

    def update(self, **kwargs):
        session = boto3.Session()
        s3 = session.resource("s3")
        for root, dirs, files in os.walk(self.directory):
            for name in files:
                path = root.split(os.path.sep)
                path.append(name)
                mimetype = mimetypes.guess_type(os.path.sep.join(path))[0]
                if mimetype is None:
                    print("Skipping file {} with no MIME type.".format(name))
                    continue
                print(mimetype + "\t" + os.path.sep.join(path))
                s3.Bucket(self.bucket_name + "-fup").upload_file(
                    os.path.sep.join(path),
                    os.path.sep.join(path[2:]),
                    ExtraArgs={
                        "ContentType": mimetype,
                        'GrantRead': 'uri="http://acs.amazonaws.com/groups/global/AllUsers"',
                    }
                )
        return self.bucket_name + "-fup"


    def status(self, **kwargs):
        return {
            "url": f"https://{self.bucket_name}-fup.s3.amazonaws.com/"
        }

    def teardown(self, **kwargs):
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(self.bucket_name)
        bucket.objects.all().delete()
        return bucket.delete()


class APIComponent(Component):

    def __init__(self, **kwargs):
        self.stack_name = kwargs['stack_name']
        try:
            self.stack_name = list(json.loads(self.stack_name).keys())[0]
        except:
            pass
        self.directory = kwargs.get('directory', "api")
        _default_config = {
            self.stack_name: {
                "s3_bucket": (
                    self.stack_name + "-api-fup"
                    if not self.stack_name.endswith('-api-fup')
                    else self.stack_name
                ),
                "app_function": "main.APP",
                "aws_region": "us-east-1",
            }
        }
        pwd = os.getcwd()
        os.chdir(self.directory)
        self.config = kwargs.get('config', _default_config)
        if self.stack_name not in self.config:
            self.config[self.stack_name] = _default_config[self.stack_name]
        with open("./zappa_settings.json", 'w') as fh:
            fh.write(json.dumps(self.config))
        os.chdir(pwd)

    def __del__(self):
        """
        Remove the zappa_settings.json tempfile.
        Arguments:
            None
        """
        pwd = os.getcwd()
        try:
            os.chdir(self.directory)
            os.remove("./zappa_settings.json")
        except Exception:
            pass
        os.chdir(pwd)

    def init(self, **kwargs):
        # create zappa file
        pwd = os.getcwd()
        os.chdir(self.directory)
        print(
            subprocess.run(
                "pip3 install -U flask zappa",
                shell=True,
                stdout=subprocess.PIPE
            ).stdout
        )
        print(
            subprocess.run(
                "pip3 install -r ./requirements.txt",
                shell=True,
                stdout=subprocess.PIPE
            ).stdout
        )
        # zappa deploy (update)
        print(
            subprocess.run(
                f"zappa deploy {self.stack_name}",
                shell=True,
                stdout=subprocess.PIPE
            ).stdout
        )
        os.chdir(pwd)
        return json.dumps(self.config)
        # return zappa config json

    def update(self, **kwargs):
        pwd = os.getcwd()
        os.chdir(self.directory)
        print(
            subprocess.run(
                "pip3 install -U flask zappa",
                shell=True,
                stdout=subprocess.PIPE
            ).stdout
        )
        print(
            subprocess.run(
                "pip3 install -r ./requirements.txt",
                shell=True,
                stdout=subprocess.PIPE
            ).stdout
        )
        print(
            subprocess.run(
                f"zappa update {self.stack_name}",
                shell=True,
                stdout=subprocess.PIPE
            ).stdout
        )
        os.chdir(pwd)
        return json.dumps(self.config)


    def status(self, **kwargs):
        pwd = os.getcwd()
        os.chdir(self.directory)
        result = (
            subprocess.run(
                f"zappa status {self.stack_name}",
                shell=True,
                stdout=subprocess.PIPE
            ).stdout
        ).decode('utf-8')
        os.chdir(pwd)
        results = {
            line.split(":")[0].strip(): ":".join(line.split(":")[1:]).strip()
            for line in result.split("\n")
            if (
                ('Invocations' in line) or
                ('Errors' in line) or
                ('Error Rate' in line) or
                ('API Gateway URL' in line)
            )
        }
        return results

    def teardown(self, **kwargs):
        pwd = os.getcwd()
        os.chdir(self.directory)
        print(
            subprocess.run(
                f"zappa undeploy -y {self.stack_name}",
                shell=True,
                stdout=subprocess.PIPE
            ).stdout
        )
        os.chdir(pwd)
