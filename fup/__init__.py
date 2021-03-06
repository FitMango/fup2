#!/usr/bin/env python3

from typing import List
import json
import sys

import boto3

import colored
from colored import stylize

from pynamodb.attributes import BooleanAttribute, UnicodeAttribute, MapAttribute, UTCDateTimeAttribute, NumberAttribute
from pynamodb.models import Model


from . import components


__version__ = "0.2.1"



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
    db_deployed = UnicodeAttribute(default="")
    api_deployed = UnicodeAttribute(default="")
    web_deployed = UnicodeAttribute(default="")


class fupclient:

    def __init__(self, **kwargs):
        self.aws_profile = kwargs.get('aws_profile', None)
        self.aws_region = kwargs.get('aws_region', 'us-east-1')
        self.verbose = kwargs.get('verbose', False)
        self.session = boto3.session.Session(
            region_name=self.aws_region,
            profile_name=self.aws_profile
        )
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

    def init(
        self, stack_name: str, component_list=FupComponents.ALL,
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

        db_deployed = "0"
        api_deployed = "0"
        web_deployed = "0"
        if FupComponents.WEB in component_list:
            self._info(f"Creating component [{stack_name}.WEB]...")
            web_deployed = components.WebComponent(
                stack_name=stack_name,
                directory=web_path
            ).init()
        if FupComponents.API in component_list:
            self._info(f"Creating component [{stack_name}.API]...")
            api_deployed = components.APIComponent(
                stack_name=stack_name,
                directory=api_path
            ).init()
        # if FupComponents.DB in component_list:
        #     self._info(f"Creating component [{stack_name}.DB]...")
        #     components.DBComponent(schemafile=db_path).init()

        new_stack = StackModel(stack_name)
        new_stack.web_deployed = web_deployed
        new_stack.api_deployed = api_deployed
        new_stack.db_deployed = db_deployed
        self._info("Uploading stack configuration...")
        new_stack.save()
        self._log(stylize(
            "Created stack [{}].".format(stack_name),
            colored.fg("green")
        ))

    def update(
        self, stack_name: str, component_list=FupComponents.ALL,
        web_path: str = "./web",
        api_path: str = "./api",
        db_path: str = "./schema.yaml"
    ) -> None:
        # Fail if stack DNE:
        if not self.stack_db.exists():
            self._warn("Stack lookup table does not exist, try `init`.")
            sys.exit(1)

        stack = self.stack_db.get(stack_name)

        if FupComponents.WEB in component_list:
            self._info(f"Updating component [{stack_name}.WEB]...")
            stack.web_deployed = components.WebComponent(
                stack_name=stack_name,
                directory=web_path
            ).update()

        if FupComponents.API in component_list:
            self._info(f"Updating component [{stack_name}.API]...")
            if (
                    (stack.api_deployed == "0") or  # placeholder falsy
                    (not stack.api_deployed) or     # actual falsy
                    (stack.api_deployed == "null")  # dynamo falsky
            ):
                stack.api_deployed = components.APIComponent(
                    stack_name=stack_name,
                    directory=api_path
                ).update()
            else:
                stack.api_deployed = components.APIComponent(
                    stack_name=stack_name,
                    directory=api_path,
                    config=json.loads(stack.api_deployed)
                ).update()

        self._info("Uploading stack configuration...")
        stack.save()
        self._success(
            "Updated stack [{}].".format(stack_name)
        )


    def status(
        self, stack_name: str, component_list=FupComponents.ALL,
        web_path: str = "./web",
        api_path: str = "./api",
        db_path: str = "./schema.yaml"
    ) -> dict:
        # Fail if stack DNE:
        if not self.stack_db.exists():
            self._warn("Stack lookup table does not exist, try `init`.")
            sys.exit(1)

        stack = self.stack_db.get(stack_name)
        outputs = {}

        if FupComponents.WEB in component_list:
            outputs['WEB'] = (
                components.WebComponent(
                    stack_name=stack_name,
                    directory=web_path
                ).status()
            )

        if FupComponents.API in component_list:
            outputs['API'] = (
                components.APIComponent(
                    stack_name=stack_name,
                    directory=api_path
                ).status()
            )
        return outputs

    def teardown(self, stack_name: str, component_list) -> bool:
        self._log(stylize(
            f"Tearing down [{stack_name}]...",
            colored.fg("red"), colored.attr('bold')
        ))
        stack = self.stack_db.get(stack_name)

        if FupComponents.DB in component_list:
            if stack.db_deployed != "0":
                # TODO: Tear down deployed assets
                pass

        if FupComponents.API in component_list:
            if stack.api_deployed != "0":
                try:
                    components.APIComponent(
                        stack_name=stack.api_deployed,
                    ).teardown()
                    stack.api_deployed = "0"
                    stack.save()
                except Exception as e:
                    raise ValueError("Could not remove API component: {}".format(e))

        if FupComponents.WEB in component_list:
            if stack.web_deployed != "0":
                try:
                    components.WebComponent(
                        stack_name=stack.web_deployed
                    ).teardown()
                    stack.web_deployed = "0"
                    stack.save()
                except Exception as e:
                    raise ValueError("Could not remove WEB component: {}".format(e))
        self._success(f"Successfully tore down stack [{stack_name}.{component_list}].")
        stack = self.stack_db.get(stack_name)
        if stack.web_deployed == stack.api_deployed == stack.db_deployed == "0":
            self._success(f"Completely removing all traces of stack [{stack_name}].")
            return stack.delete()
            self._success("Done!")
        else:
            return False

    def get_stacks(self) -> List[str]:
        try:
            return [
                i.stack_name for i in self.stack_db.scan()
            ]
        except:
            return []

