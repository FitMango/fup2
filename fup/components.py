import abc
from abc import abstractmethod

import mimetypes
import os
from uuid import uuid4

import yaml

import boto3
from pynamodb.attributes import BooleanAttribute, UnicodeAttribute, MapAttribute, UTCDateTimeAttribute, NumberAttribute
from pynamodb.models import Model



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
        self.bucket_name = kwargs['app_name']
        self.directory = kwargs.get('directory')

        self.website_configuration = {
            'ErrorDocument': {'Key': 'index.html'},
            'IndexDocument': {'Suffix': 'index.html'},
        }

    def init(self, **kwargs):
        # create the bucket
        self.bucket = self.client.create_bucket(
            Bucket=self.bucket_name,
            ACL='public-read'
        )
        self.client.put_bucket_website(
            Bucket=self.bucket_name,
            WebsiteConfiguration=self.website_configuration
        )
        self.update()
        return self.bucket_name

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
                s3.Bucket(self.bucket_name).upload_file(
                    os.path.sep.join(path),
                    os.path.sep.join(path[2:]),
                    ExtraArgs={
                        "ContentType": mimetype,
                        'GrantRead': 'uri="http://acs.amazonaws.com/groups/global/AllUsers"',
                    }
                )
        return self.bucket_name


    def status(self, **kwargs):
        return {
            "url": f"https://{self.stack_name}.s3.amazonaws.com/"
        }

    def teardown(self, **kwargs):
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(self.bucket_name)
        bucket.objects.all().delete()
        return bucket.delete()

class DBComponent(Component):

    def __init__(self, **kwargs):
        pass


class APIComponent(Component):

    def __init__(self, **kwargs):
        pass
