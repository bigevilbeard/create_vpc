import os
import boto3
from botocore.exceptions import WaiterError

def create_vpc(ec2_resource, vpc_cidr_block, vpc_name):
    with ec2_resource.create_vpc(CidrBlock=vpc_cidr_block) as vpc:
        vpc.create_tags(Tags=[{"Key": "Name", "Value": vpc_name}])
        try:
            vpc.get_waiter('vpc_available').wait(VpcIds=[vpc.id])
        except WaiterError as e:
            print(f"Error waiting for VPC availability: {e}")
            return None
        else:
            print(f"VPC {vpc_name} created with ID: {vpc.id}")
            return vpc

def create_internet_gateway(ec2_resource, vpc):
    with ec2_resource.create_internet_gateway() as ig:
        vpc.attach_internet_gateway(InternetGatewayId=ig.id)
        print(f"Internet Gateway attached with ID: {ig.id}")
        return ig

def create_route_table(vpc, internet_gateway):
    with vpc.create_route_table() as route_table:
        route_table.create_route(
            DestinationCidrBlock='0.0.0.0/0',
            GatewayId=internet_gateway.id
        )
        print(f"Route table created with ID: {route_table.id}")
        return route_table

def create_subnet(ec2_resource, vpc, subnet_cidr_block):
    with ec2_resource.create_subnet(CidrBlock=subnet_cidr_block, VpcId=vpc.id) as subnet:
        print(f"Subnet created with ID: {subnet.id}")
        return subnet

def associate_route_table(route_table, subnet):
    route_table.associate_with_subnet(SubnetId=subnet.id)
    print("Route table associated with subnet")

def main():
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    aws_region = os.environ.get('AWS_REGION', 'us-east-1')

    ec2 = boto3.resource('ec2', aws_access_key_id=aws_access_key_id,
                         aws_secret_access_key=aws_secret_access_key,
                         region_name=aws_region)

    vpc = create_vpc(ec2, '192.168.0.0/16', 'my_vpc')
    if vpc:
        internet_gateway = create_internet_gateway(ec2, vpc)
        route_table = create_route_table(vpc, internet_gateway)
        subnet = create_subnet(ec2, vpc, '192.168.1.0/24')
        associate_route_table(route_table, subnet)

if __name__ == "__main__":
    main()
