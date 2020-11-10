import json
import boto3

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Orders')
    
    req = event['body']
    if isinstance(req, str):
        req = json.loads(req)
    # print(f"Event Recieved: {req}")
    # print(f"Ctx: {context}")

    table.put_item(
    Item={
        'OrderOwner': req['order_owner'],
        'CustomerName': req['customer_name'],
        'Address': req['address'],
        'BagsPurchased': req['bags'],
        'BagsToSpread': req['bags_to_spread'],
    })

    return {
        'statusCode': 200,
        'body': json.dumps('Order Entered!'),
        'headers': {
            'Access-Control-Allow-Origin': '*',
        },
    }
