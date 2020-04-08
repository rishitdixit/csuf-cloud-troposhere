import troposphere.ec2 as ec2
import boto3, logging
from troposphere import FindInMap, Template, Parameter, Ref, GetAtt,  Output
from botocore.exceptions import ClientError


template = Template()

template.set_version("2010-09-09")
template.set_description( "CSUF AWS CloudFormation Template: EC2 Instance With Ephemeral Drives - Template that attaches ephemeral drives using EC2 block device mappings. **WARNING** This template creates an Amazon EC2 instance. There will be charges for the AWS resources used if you create a stack from this template.")

instance_name_param = template.add_parameter(Parameter(
    "InstanceNameTag",
    Description="Name of your instance",
    Type="String",
    MaxLength = "255",
    MinLength = "1"
))

cost_center_param = template.add_parameter(Parameter(
    "CostCenterTag",
    Description="Cost Center to bill to",
    Type="String",
    MaxLength = "255",
    MinLength = "1"
))

owner_param = template.add_parameter(Parameter(
    "OwnerTag",
    Description="Owner of the resource",
    Type="String",
    MaxLength = "255",
    MinLength = "1",
    ConstraintDescription = "must enter as first name.last name"
))

technical_contact_param = template.add_parameter(Parameter(
    "TechnicalContactTag",
    Description="Technical contact of the resource",
    Type="String",
    MaxLength = "255",
    MinLength = "1",
    ConstraintDescription = "must enter as first name.last name"
))

data_classfication_param = template.add_parameter(Parameter(
    "DataClassificationTag",
    Description="Technical contact of the resource",
    Type="String",
    MaxLength = "255",
    MinLength = "1"
))

environment_param = template.add_parameter(Parameter(
    "EnvironmentTag",
    Description="Type of environment the resource is provisioned to",
    Type="String",
    MaxLength = "255",
    MinLength = "1"
))

department_param = template.add_parameter(Parameter(
    "DepartmentTag",
    Description="Type of environment the resource is provisioned to",
    Type="String",
    MaxLength = "255",
    MinLength = "1"
))

project_param = template.add_parameter(Parameter(
    "ProjectTag",
    Description="Abbreviated or abstract name of project",
    Type="String",
    MaxLength = "255",
    MinLength = "1"
))


service_param = template.add_parameter(Parameter(
    "ServiceTag",
    Description="Service that the resource provides",
    Type="String",
    MaxLength = "255",
    MinLength = "1"
))

shutdown_policy_param = template.add_parameter(Parameter(
    "ShutdownPolicyTag",
    Description="Schedule in which the resource should be disabled or powered off",
    Type="String",
    MaxLength = "255",
    MinLength = "1"
))

key_name_with_str_param = template.add_parameter(Parameter(
    "KeyName",
    Description="Name of an existing EC2 KeyPair to enable SSH access to the instances",
    Type="String",
    MaxLength = "255",
    MinLength = "1",
    AllowedPattern="[\\x20-\\x7E]*",
    ConstraintDescription="can contain only ASCII characters."
))

key_name_with_str_key_pair_str = template.add_parameter(Parameter(
    "KeyNameWithKeyPairTag",
    Description="Name of an existing EC2 KeyPair to enable SSH access to the web server",
    Type="AWS::EC2::KeyPair::KeyName",
    ConstraintDescription="must be the name of an existing EC2 KeyPair."
))

instance_type_param = template.add_parameter(Parameter(
    "InstanceType",
    Description="WebServer EC2 instance type",
    Type="String",
    AllowedValues = [ "a1.medium", "a1.large", "a1.xlarge", "a1.2xlarge", "a1.4xlarge", "m4.large", "m4.xlarge", "m4.2xlarge", "m4.4xlarge", "m4.10xlarge", "m5.large", "m5.xlarge", "m5.2xlarge", "m5.4xlarge", "m5.8xlarge", "m5.12xlarge", "m5.16xlarge", "m5.24xlarge", "m5a.large", "m5a.xlarge", "m5a.2xlarge", "m5a.4xlarge", "m5a.8xlarge", "m5a.12xlarge", "m5a.16xlarge", "m5a.24xlarge", "m5ad.large", "m5ad.xlarge", "m5ad.2xlarge", "m5ad.4xlarge", "m5ad.8xlarge", "m5ad.12xlarge", "m5ad.16xlarge", "m5ad.24xlarge", "m5d.large", "m5d.xlarge", "m5d.2xlarge", "m5d.4xlarge", "m5d.8xlarge", "m5d.12xlarge", "m5d.16xlarge", "m5d.24xlarge", "m5dn.large", "m5dn.xlarge", "m5dn.2xlarge", "m5dn.4xlarge", "m5dn.8xlarge", "m5dn.12xlarge", "m5dn.16xlarge", "m5dn.24xlarge", "m5n.large", "m5n.xlarge", "m5n.2xlarge", "m5n.4xlarge", "m5n.8xlarge", "m5n.12xlarge", "m5n.16xlarge", "m5n.24xlarge", "t2.nano", "t2.micro", "t2.small", "t2.medium", "t2.large", "t2.xlarge", "t2.2xlarge", "t3.nano", "t3.micro", "t3.small", "t3.medium", "t3.large", "t3.xlarge", "t3.2xlarge", "t3a.nano", "t3a.micro", "t3a.small", "t3a.medium", "t3a.large", "t3a.xlarge", "t3a.2xlarge"],
    ConstraintDescription="must be a valid EC2 instance type.",
    Default =  "t2.micro"
))

ssh_location_param = template.add_parameter(Parameter(
    "SSHLocation",
    Description="Lockdown SSH access to the bastion host (default can be accessed from anywhere)",
    Type="String",
    MaxLength = "18",
    MinLength = "9",
    Default="0.0.0.0/0",
    AllowedPattern="(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})/(\\d{1,2})",
    ConstraintDescription="must be a valid CIDR range of the form x.x.x.x/x."
))

template.add_mapping("AWSInstanceType2Arch", {
      "a1.medium":{"Arch" : "HVM64"},
      "a1.large":{"Arch":"HVM64"},
      "a1.xlarge":{"Arch":"HVM64"},
      "a1.2xlarge":{"Arch":"HVM64"},
      "a1.4xlarge":{"Arch" :"HVM64"},
      "t2.nano":{"Arch" : "HVM64"  },
      "t2.micro"    : { "Arch" : "HVM64"  },
      "t2.small"    : { "Arch" : "HVM64"  },
      "t2.medium"   : { "Arch" : "HVM64"  },
      "t2.large"    : { "Arch" : "HVM64"  },
      "m1.small"    : { "Arch" : "HVM64"  },
      "m1.medium"   : { "Arch" : "HVM64"  },
      "m1.large"    : { "Arch" : "HVM64"  },
      "m1.xlarge"   : { "Arch" : "HVM64"  },
      "m2.xlarge"   : { "Arch" : "HVM64"  },
      "m2.2xlarge"  : { "Arch" : "HVM64"  },
      "m2.4xlarge"  : { "Arch" : "HVM64"  },
      "m3.medium"   : { "Arch" : "HVM64"  },
      "m3.large"    : { "Arch" : "HVM64"  },
      "m3.xlarge"   : { "Arch" : "HVM64"  },
      "m3.2xlarge"  : { "Arch" : "HVM64"  },
      "m4.large"    : { "Arch" : "HVM64"  },
      "m4.xlarge"   : { "Arch" : "HVM64"  },
      "m4.2xlarge"  : { "Arch" : "HVM64"  },
      "m4.4xlarge"  : { "Arch" : "HVM64"  },
      "m4.10xlarge" : { "Arch" : "HVM64"  },
      "c1.medium"   : { "Arch" : "HVM64"  },
      "c1.xlarge"   : { "Arch" : "HVM64"  },
      "c3.large"    : { "Arch" : "HVM64"  },
      "c3.xlarge"   : { "Arch" : "HVM64"  },
      "c3.2xlarge"  : { "Arch" : "HVM64"  },
      "c3.4xlarge"  : { "Arch" : "HVM64"  },
      "c3.8xlarge"  : { "Arch" : "HVM64"  },
      "c4.large"    : { "Arch" : "HVM64"  },
      "c4.xlarge"   : { "Arch" : "HVM64"  },
      "c4.2xlarge"  : { "Arch" : "HVM64"  },
      "c4.4xlarge"  : { "Arch" : "HVM64"  },
      "c4.8xlarge"  : { "Arch" : "HVM64"  },
      "g2.2xlarge"  : { "Arch" : "HVMG2"  },
      "g2.8xlarge"  : { "Arch" : "HVMG2"  },
      "r3.large"    : { "Arch" : "HVM64"  },
      "r3.xlarge"   : { "Arch" : "HVM64"  },
      "r3.2xlarge"  : { "Arch" : "HVM64"  },
      "r3.4xlarge"  : { "Arch" : "HVM64"  },
      "r3.8xlarge"  : { "Arch" : "HVM64"  },
      "i2.xlarge"   : { "Arch" : "HVM64"  },
      "i2.2xlarge"  : { "Arch" : "HVM64"  },
      "i2.4xlarge"  : { "Arch" : "HVM64"  },
      "i2.8xlarge"  : { "Arch" : "HVM64"  },
      "d2.xlarge"   : { "Arch" : "HVM64"  },
      "d2.2xlarge"  : { "Arch" : "HVM64"  },
      "d2.4xlarge"  : { "Arch" : "HVM64"  },
      "d2.8xlarge"  : { "Arch" : "HVM64"  },
      "hi1.4xlarge" : {"Arch":"HVM64"},
      "hs1.8xlarge" : {"Arch":"HVM64"},
      "cr1.8xlarge":{"Arch":"HVM64"},
      "cc2.8xlarge":{"Arch":"HVM64"}
    })

template.add_mapping("AWSInstanceType2NATArch",{
      "t1.micro"    : { "Arch" : "NATHVM64"  },
      "t2.nano"     : { "Arch" : "NATHVM64"  },
      "t2.micro"    : { "Arch" : "NATHVM64"  },
      "t2.small"    : { "Arch" : "NATHVM64"  },
      "t2.medium"   : { "Arch" : "NATHVM64"  },
      "t2.large"    : { "Arch" : "NATHVM64"  },
      "m1.small"    : { "Arch" : "NATHVM64"  },
      "m1.medium"   : { "Arch" : "NATHVM64"  },
      "m1.large"    : { "Arch" : "NATHVM64"  },
      "m1.xlarge"   : { "Arch" : "NATHVM64"  },
      "m2.xlarge"   : { "Arch" : "NATHVM64"  },
      "m2.2xlarge"  : { "Arch" : "NATHVM64"  },
      "m2.4xlarge"  : { "Arch" : "NATHVM64"  },
      "m3.medium"   : { "Arch" : "NATHVM64"  },
      "m3.large"    : { "Arch" : "NATHVM64"  },
      "m3.xlarge"   : { "Arch" : "NATHVM64"  },
      "m3.2xlarge"  : { "Arch" : "NATHVM64"  },
      "m4.large"    : { "Arch" : "NATHVM64"  },
      "m4.xlarge"   : { "Arch" : "NATHVM64"  },
      "m4.2xlarge"  : { "Arch" : "NATHVM64"  },
      "m4.4xlarge"  : { "Arch" : "NATHVM64"  },
      "m4.10xlarge" : { "Arch" : "NATHVM64"  },
      "c1.medium"   : { "Arch" : "NATHVM64"  },
      "c1.xlarge"   : { "Arch" : "NATHVM64"  },
      "c3.large"    : { "Arch" : "NATHVM64"  },
      "c3.xlarge"   : { "Arch" : "NATHVM64"  },
      "c3.2xlarge"  : { "Arch" : "NATHVM64"  },
      "c3.4xlarge"  : { "Arch" : "NATHVM64"  },
      "c3.8xlarge"  : { "Arch" : "NATHVM64"  },
      "c4.large"    : { "Arch" : "NATHVM64"  },
      "c4.xlarge"   : { "Arch" : "NATHVM64"  },
      "c4.2xlarge"  : { "Arch" : "NATHVM64"  },
      "c4.4xlarge"  : { "Arch" : "NATHVM64"  },
      "c4.8xlarge"  : { "Arch" : "NATHVM64"  },
      "g2.2xlarge"  : { "Arch" : "NATHVMG2"  },
      "g2.8xlarge"  : { "Arch" : "NATHVMG2"  },
      "r3.large"    : { "Arch" : "NATHVM64"  },
      "r3.xlarge"   : { "Arch" : "NATHVM64"  },
      "r3.2xlarge"  : { "Arch" : "NATHVM64"  },
      "r3.4xlarge"  : { "Arch" : "NATHVM64"  },
      "r3.8xlarge"  : { "Arch" : "NATHVM64"  },
      "i2.xlarge"   : { "Arch" : "NATHVM64"  },
      "i2.2xlarge"  : { "Arch" : "NATHVM64"  },
      "i2.4xlarge"  : { "Arch" : "NATHVM64"  },
      "i2.8xlarge"  : { "Arch" : "NATHVM64"  },
      "d2.xlarge"   : { "Arch" : "NATHVM64"  },
      "d2.2xlarge"  : { "Arch" : "NATHVM64"  },
      "d2.4xlarge"  : { "Arch" : "NATHVM64"  },
      "d2.8xlarge"  : { "Arch" : "NATHVM64"  },
      "hi1.4xlarge" : { "Arch" : "NATHVM64"  },
      "hs1.8xlarge" : { "Arch" : "NATHVM64"  },
      "cr1.8xlarge" : { "Arch" : "NATHVM64"  },
      "cc2.8xlarge" : { "Arch" : "NATHVM64"  }
    })

template.add_mapping("AWSRegionArch2AMI",  {
      "us-east-1"   : {"HVM64" : "ami-0080e4c5bc078760e", "HVMG2" : "ami-0aeb704d503081ea6"},
      "us-west-2"   : {"HVM64" : "ami-01e24be29428c15b2", "HVMG2" : "ami-0fe84a5b4563d8f27"},
      "us-west-1"   : {"HVM64" : "ami-0ec6517f6edbf8044", "HVMG2" : "ami-0a7fc72dc0e51aa77"}
    })

security_group_resource = template.add_resource(
    ec2.SecurityGroup(
        "EC2SecurityGroup",
        GroupDescription="SSH access",
        SecurityGroupIngress=[
            ec2.SecurityGroupRule(
                IpProtocol="tcp",
                FromPort="22",
                ToPort="22",
                CidrIp=Ref(ssh_location_param),
            )
        ]
    )
)

ec2_instance = template.add_resource(ec2.Instance(
    "Ec2Instance",
    KeyName=Ref(key_name_with_str_key_pair_str),
    InstanceType = Ref(instance_type_param),
    SecurityGroups= Ref(security_group_resource),
    ImageId = FindInMap("AWSRegionArch2AMI", Ref("AWS::Region"),FindInMap("AWSRegionArch2AMI", Ref("AWS::InstanceType"),"Arch")),
    BlockDeviceMappings=[
        ec2.BlockDeviceMapping(
            DeviceName="/dev/sdc",
            VirtualName="ephemeral0")
    ]
))

template.add_output(
    [Output('Instance',
            Description="DNS Name of the newly created EC2 instance",
            Value=GetAtt("EC2Instance", "PublicDnsName"))])

print(template.to_json())

# f = open("gp-ec2.cform","a")
# f.write(template.to_json())
# f.close()
#
# client = boto3.client('s3')
# try:
#     response = client.upload_file("gp-ec2.cform", "csuf-cloud-formation","gp-ec2.cform")
# except ClientError as e:
#         logging.error(e)


