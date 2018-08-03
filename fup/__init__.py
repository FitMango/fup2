#!/usr/bin/env python3

from typing import List
import sys

import boto3

import colored
from colored import stylize

from pynamodb.attributes import BooleanAttribute, UnicodeAttribute, MapAttribute, UTCDateTimeAttribute, NumberAttribute
from pynamodb.models import Model


from . import components


__version__ = "0.2.0"



class FupComponents:
    DB = "DB"
    API = "API"
    WEB = "WEB"
    ALL = ["DB", "API", "WEB"]

    @staticmethod
    def csv_to_components(csv: str) -> List[str]:
        csv = csv.upper()
        cs = []
        if FupComponents.DB in csv.split(","):
            cs.append(FupComponents.DB)
        if FupComponents.WEB in csv.split(","):
            cs.append(FupComponents.WEB)
        if FupComponents.API in csv.split(","):
            cs.append(FupComponents.API)
        return cs

    @staticmethod
    def get_component_class(name: str):
        return {
            FupComponents.DB: components.DBComponent,
            FupComponents.WEB: components.WebComponent,
            FupComponents.API: components.APIComponent,
        }[name]


class StackModel(Model):

    class Meta:
        table_name = "_fup_stacks"

    stack_name = UnicodeAttribute(hash_key=True)
    schema = MapAttribute(null=True)
    db_deployed = BooleanAttribute(default=False)
    api_deployed = BooleanAttribute(default=False)
    web_deployed = BooleanAttribute(default=False)


class fupclient:

    def __init__(self, **kwargs):
        self.aws_profile = kwargs.get('aws_profile', None)
        self.aws_region = kwargs.get('aws_region', 'us-east-1')
        self.verbose = kwargs.get('verbose', False)
        self.session = boto3.session.Session(
            region_name=self.aws_region,
            profile_name=self.aws_profile
        )
        # self.session.resource('dynamodb')
        self.stack_db = StackModel

    def _log(self, msg: str, level=0):
        if self.verbose:
            print(msg)

    def _info(self, msg):
        self._log(stylize(
            msg,
            colored.fg("blue")
        ))

    def _warn(self, msg):
        self._log(stylize(
            msg,
            colored.fg("yellow")
        ))

    def _success(self, msg):
        self._log(stylize(
            msg,
            colored.fg("green")
        ))

    def _create_stack_lookup_table(self):
        self.stack_db.create_table(
            read_capacity_units=1,
            write_capacity_units=1,
            wait=True
        )

    def stack_exists(self, stack_name: str) -> bool:
        if self.stack_db.get(stack_name):
            return True
        return False

    def teardown(self, stack_name: str) -> bool:
        self._log(stylize(
            f"Tearing down [{stack_name}]...",
            colored.fg("red"), colored.attr('bold')
        ))
        # TODO: Tear down deployed assets
        stack = self.stack_db.get(stack_name)
        if stack.db_deployed:
            # TODO: Tear down deployed assets
            pass
        self._success(f"Successfully tore down stack [{stack_name}].")
        return stack.delete()

    def get_stacks(self, pending=None):
        try:
            if pending is None:
                response = [
                    i.stack_name for i in self.stack_db.scan()
                ]
            else:
                response = [
                    i.stack_name for i in self.stack_db.scan(
                        self.stack_db.api_deployed != pending
                    )
                ]
            return response
        except:
            return []

    def init(
        self, stack_name: str, component_list=[FupComponents.ALL],
        web_path: str = "./web",
        api_path: str = "./api",
        db_path: str = "./schema.yaml"
    ) -> None:
        # Create the new stack. Fail if it already exists in the database:
        if not self.stack_db.exists():
            self._warn("Stack lookup table does not exist, creating now...")
            self._create_stack_lookup_table()
            self._info("Stack lookup table created.")

        self._info(f"Creating stack [{stack_name}]...")
        try:
            self.stack_db.get(stack_name)
            raise ValueError()
        except ValueError:
            self._log(stylize(
                "Stack [{}] already exists.".format(stack_name),
                colored.fg("red")
            ))
            sys.exit(1)
        except:
            pass

        if FupComponents.DB in component_list:
            self._info(f"Creating component [{stack_name}.DB]...")
            components.DBComponent(schemafile=db_path).init()

        new_stack = StackModel(stack_name)
        new_stack.save()
        self._log(stylize(
            "Created stack [{}].".format(stack_name),
            colored.fg("green")
        ))
