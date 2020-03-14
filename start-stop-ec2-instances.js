// Demonstration video can be found at: https://youtu.be/roAerKVfq-Y

// StopEC2Instance

const AWS = require('aws-sdk');

exports.handler = (event, context, callback) => {
    const ec2 = new AWS.EC2({ region: event.instanceRegion });
    
    ec2.stopInstances({ InstanceIds: [event.instanceId] }).promise()
        .then(() => callback(null, `Successfully stopped ${event.instanceId}`))
        .catch(err => callback(err));
};

// StartEC2Instance

const AWS = require('aws-sdk');

exports.handler = (event, context, callback) => {
    const ec2 = new AWS.EC2({ region: event.instanceRegion });
    
    ec2.startInstances({ InstanceIds: [event.instanceId] }).promise()
        .then(() => callback(null, `Successfully started ${event.instanceId}`))
        .catch(err => callback(err));
};