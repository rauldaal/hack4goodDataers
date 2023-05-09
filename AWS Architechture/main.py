# + ------------------------------------------
# Description:
# This is the main file for the AWS Hackathon
# + ------------------------------------------

# + ------------------------------------------
# Imports
# + ------------------------------------------

from constructs import Construct
from aws_cdk import App, Stack, Environment
from hackathon import Hackathon
import os

# + ------------------------------------------
# Global Variables
# + ------------------------------------------

"""
export AWS_ACCOUNT_ID="221829447095"
export AWS_REGION="eu-south-2"
"""

AWS_ACCOUNT_ID = os.environ["AWS_ACCOUNT_ID"] 
AWS_REGION = os.environ["AWS_REGION"]

# + ------------------------------------------
# Main
# + ------------------------------------------

app = App()

env = Environment(account=AWS_ACCOUNT_ID, region=AWS_REGION)

hackathon_stack = Hackathon(
    scope=Stack(app, "MyHackathonStack", env=env),
    id="MyHackathonStack",
    env=env,
)

hackathon_stack.deploy_iam_users()
hackathon_stack.deploy_iam_roles()
hackathon_stack.deploy_vpc()
hackathon_stack.deploy_ec2_instance()
hackathon_stack.deploy_rds_instance()
hackathon_stack.deploy_secrets_manager()
hackathon_stack.deploy_cloudformation_stack()
hackathon_stack.deploy_cloudwatch_dashboard()

app.synth()

# + ------------------------------------------
# cdk deploy MyHackathonStack/MyHackathonStack
# + ------------------------------------------