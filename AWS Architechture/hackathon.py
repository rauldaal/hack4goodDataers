# + ------------------------------------------
# Description:
#   This will contain the Hackathon class.
#   It will be used to deploy the VPC, EC2 instance, Aurora DB, etc.
# + ------------------------------------------

# + ------------------------------------------
# Imports
# + ------------------------------------------

from aws_cdk import (
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_cloudformation as cfn,
    RemovalPolicy,
    aws_secretsmanager as secretsmanager,
    Stack,
    aws_iam as iam,
    SecretValue
)
from constructs import Construct

# + ------------------------------------------
# Functions
# + ------------------------------------------

class Hackathon(Stack):
    
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

    def deploy_iam_users(self):

        # We need to create Client user and Business user
        # Client user will have access to the EC2 instance
        # Business user will have access to insert data into the database 
        # and just delete and read data inserted by this user

        # Create the Administrator user (will have access to Manage Ec2 and RDS instances)
        self.admin_user = iam.User(
            self,
            "MyAdminUser",
            user_name="admin_user",
            password=SecretValue.plain_text("admin_user_password"),
            password_reset_required=True,
        )

        # Create the Business user
        self.business_user = iam.User(
            self,
            "MyBusinessUser",
            user_name="business_user",
            password=SecretValue.plain_text("business_user_password"),
            password_reset_required=True,
        )

    def deploy_iam_roles(self):

        # Create the Administrator role (for admins)
        self.client_role = iam.Role(
            self,
            "AdminRole",
            assumed_by=(
                iam.WebIdentityPrincipal("cognito-identity.amazonaws.com"),
                iam.ServicePrincipal("ec2.amazonaws.com"),
                iam.ServicePrincipal("rds.amazonaws.com")
            )
        )

        # Create the Business role (for supermarkets)
        self.business_role = iam.Role(
            self,
            "MyBusinessRole",
            assumed_by=iam.WebIdentityPrincipal("rds.amazonaws.com")
        )

    def deploy_vpc(self):

        # Crea la VPC
        self.vpc = ec2.Vpc(
            self,
            "MyVPC",
            cidr="10.0.0.0/16",
            max_azs=2,
            nat_gateways=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public", subnet_type=ec2.SubnetType.PUBLIC, cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="Private", subnet_type=ec2.SubnetType.PRIVATE, cidr_mask=24
                ),
            ],
        )

        # Crea un Internet Gateway y lo asocia con la VPC
        self.igw = ec2.CfnInternetGateway(self, "MyInternetGateway")
        self.attach_igw = ec2.CfnVPCGatewayAttachment(
            self, "MyAttachGateway", vpc_id=self.vpc.vpc_id, internet_gateway_id=self.igw.ref
        )

        # Crea un security group para la instancia EC2
        self.ec2_sg = ec2.SecurityGroup(
            self,
            "MyEC2SecurityGroup",
            vpc=self.vpc,
            allow_all_outbound=True,
        )

        # Crea un security group para la base de datos
        self.db_sg = ec2.SecurityGroup(
            self,
            "MyDBSecurityGroup",
            vpc=self.vpc,
            allow_all_outbound=True,
        )

    def deploy_ec2(self):

        # Crea la instancia EC2
        self.ec2_instance_1 = ec2.Instance(
            self,
            "MyInstance1",
            instance_type=ec2.InstanceType("gravity.medium"),
            machine_image=ec2.MachineImage.latest_amazon_linux(),
            vpc=self.vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            security_group=self.ec2_sg,
        )

        self.ec2_instance_2 = ec2.Instance(
            self,
            "MyInstance2",
            instance_type=ec2.InstanceType("gravity.medium"),
            machine_image=ec2.MachineImage.latest_amazon_linux(),
            vpc=self.vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            security_group=self.ec2_sg,
        )

        # Crea el Load Balancer
        self.lb = elbv2.ApplicationLoadBalancer(
            self,
            "MyLoadBalancer",
            vpc=self.vpc,
            internet_facing=True,
            security_group=self.ec2_sg,
        )

        # Crea el target group para el Load Balancer
        self.target_group = elbv2.ApplicationTargetGroup(
            self,
            "MyTargetGroup",
            vpc=self.vpc,
            port=80,
            protocol=elbv2.ApplicationProtocol.HTTP,
            targets=[self.ec2_instance_1, self.ec2_instance_2],
            target_type=elbv2.TargetType.INSTANCE,
        )

        # Agrega las instancias EC2 al target group
        self.target_group.add_target(self.ec2_instance_1)
        self.target_group.add_target(self.ec2_instance_2)

    def deploy_aurora_db(self):
    
        # Crea el security group para la Aurora DB
        self.aurora_sg = ec2.SecurityGroup(
            self,
            "MyAuroraDBSecurityGroup",
            vpc=self.vpc,
            allow_all_outbound=True,
        )
        
        # Crea el subgrupo para las subnets de la Aurora DB
        self.db_subnet_group = rds.CfnDBSubnetGroup(
            self,
            "MyDBSubnetGroup",
            subnet_ids=self.vpc.select_subnets(subnet_type=ec2.SubnetType.PRIVATE).subnet_ids,
            db_subnet_group_name="MyDBSubnetGroup",
            description="Subnets to launch my Aurora DB instance"
        )
        
        # Crea la instancia de la Aurora DB
        self.db_cluster = rds.DatabaseCluster(
            self,
            "MyDBCluster",
            engine=rds.DatabaseClusterEngine.AURORA,
            instance_props=rds.InstanceProps(
                instance_type=ec2.InstanceType("t2.micro"),
                vpc=self.vpc,
                vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE),
                security_groups=[self.aurora_sg]
            ),
            default_database_name="my_db",
            instances=2,
            subnet_group=self.db_subnet_group,
            removal_policy=RemovalPolicy.DESTROY
        )
