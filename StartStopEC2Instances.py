# boto3 is a Python library maintained by Amazon itself. It's totally compatible with AWS services.
# Referneces:
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#client
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rds.html#client
import boto3
import traceback

ec2 = boto3.client('ec2')
rds = boto3.client('rds')

# Note for beginner: Python is an indentation sensitive language.

def lambda_handler(event, context):

    try:
        start_stop_ec2_instances(event, context)
        
        start_stop_rds_instances(event, context)
        
    except Exception as e:
            displayException(e)
            traceback.print_exc()
            
def start_stop_ec2_instances(event, context):
    
    # Get action parameter from event
    action = event.get('action')
    
    if action is None:
        action = ''

    # Check action
    if action.lower() not in ['start', 'stop']:
        print ("action was neither start nor stop. start_stop_ec2_instances aborted.")
    else:
        # Get ec2 instances which match filter conditions
        filtered_ec2 = ec2.describe_instances(
            Filters=[
                {'Name': 'tag-key', 'Values': ['Auto-StartStop-Enabled', 'auto-startstop-enabled']},
                {'Name': 'instance-state-name', 'Values': ['running', 'stopped']}
            ]
        ).get(
            'Reservations', []
        )
    
        # Convert array of array to a flat array
        instances_ec2 = sum(
            [
                [i for i in r['Instances']]
                for r in filtered_ec2
            ], [])
    
        print ("Found " + str(len(instances_ec2)) + " EC2 instances that can be started/stopped")
    
        # Loop through instances
        for instance_ec2 in instances_ec2:

            try:
                instance_id = instance_ec2['InstanceId']

                # Get ec2 instance name tag
                for tag in instance_ec2['Tags']:
                    if tag['Key'] == 'Name':
                        instance_name = tag['Value']
                        print ("instance_name: " + instance_name + " instance_id: " + instance_id)
                        continue
                    
                # Get ec2 instance current status
                instance_state = instance_ec2['State']['Name']
                print ("Current instance_state: %s" % instance_state)
                
                # Start or stop ec2 instance
                if instance_state == 'running' and action == 'stop':
                    ec2.stop_instances(
                        InstanceIds=[
                            instance_id
                            ],
                        # DryRun = True
                        )
                    print ("Instance %s comes to stop" % instance_id)
                    
                elif instance_state == 'stopped' and action == 'start':
                    ec2.start_instances(
                        InstanceIds=[
                            instance_id
                            ],
                        # DryRun = True
                        )
                    print ("Instance %s comes to start" % instance_id)
                    
                else:
                    print ("Instance %s(%s) status is not right to start or stop" % (instance_id, instance_name))
                
            except Exception as e:
                displayException(e)
                # traceback.print_exc()

# Caution: RDS instance will be started by AWS automatically after it is down for 7 days
def start_stop_rds_instances(event, context):

    # Get action parameter from event
    action = event.get('action')

    if action is None:
        action = ''

    # Check action
    if action.lower() not in ['start', 'stop']:
        print ("action was neither start nor stop. start_stop_rds_instances aborted.")
    else:
        # Get all of rds instances
        instances_rds = rds.describe_db_instances().get('DBInstances', [])
    
        print ("Found " + str(len(instances_rds)) + " RDS instances")
    
        # Loop through instances
        for instance_rds in instances_rds:

            try:
                instance_state = instance_rds['DBInstanceStatus']
                instance_id = instance_rds['DBInstanceIdentifier']

                # Get rds instance tags
                tags = rds.list_tags_for_resource(ResourceName = instance_rds['DBInstanceArn']).get('TagList',[])

                for tag in tags:
                    # Filter instances based on tag
                    if tag['Key'] == 'Auto-StartStop-Enabled':
        
                        print ("Current instance_state of %s is %s" % (instance_id, instance_state))
                
                        # Start or stop instance
                        if instance_state == 'available' and action == 'stop':
                            rds.stop_db_instance(
                                DBInstanceIdentifier = instance_id,
                                # DryRun = True
                            )
                            print ("Instance %s comes to stop" % instance_id)
                    
                        elif instance_state == 'stopped' and action == 'start':
                            rds.start_db_instance(
                                DBInstanceIdentifier = instance_id,
                                # DryRun = True
                            )
                            print ("Instance %s comes to start" % instance_id)
                            
                        else:
                            print ("Instance %s status is not right to start or stop" % instance_id)
                            
            except Exception as e:
                displayException(e)
                # traceback.print_exc()
            

def displayException(exception):
    exception_type = exception.__class__.__name__ 
    exception_message = str(exception) 

    print("Exception type: %s; Exception message: %s;" % (exception_type, exception_message))
