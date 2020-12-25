import json
import boto3
from decimal import Decimal
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from datetime import datetime

def json_default_encoder(obj):
     if isinstance(obj, Decimal):
        if obj % 1 > 0:
           return float(obj)
        else:
            return int(obj)
     raise TypeError("Object of type '%s' is not JSON serializable" % type(obj).__name__)

def add_or_insert(table, req):
    update_expr = []
    expr_attr = {}
    req['lastModifyTime'] = f"{datetime.utcnow().isoformat(timespec='seconds')}Z"
    for k, v in req.items():
        if 'orderId'== k or 'orderOwner' == k: continue
        update_expr.append(f'{k}=:{k}')
        expr_attr[f':{k}'] = v

    update_expr = f'SET {", ".join(update_expr)}'    
    
    print(f"Update Expr: {update_expr}")
    print(f"ExprAttr: {json.dumps(expr_attr, default=json_default_encoder)}")
    try:
        table.update_item(
            Key={
                'orderOwner': req['orderOwner'],
                'orderId': req['orderId']
            },
            UpdateExpression=update_expr,
            ExpressionAttributeValues=expr_attr,
            ReturnValues="NONE"
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
        raise

def delete_order(table, req):
    try:
        table.delete_item(
            Key={
                'orderOwner': req['orderOwner'],
                'orderId': req['orderId']
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
        raise

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('T27FundraiserOrders')

    req = event['body']
    if isinstance(req, str):
        req = json.loads(req, parse_float=Decimal)

    if 'orderOwner' not in req or 'orderId' not in req:
        return {
            'statusCode': 400,
            'body': 'Request must contain orderId and orderOwner fields',
            'headers': {
                'Access-Control-Allow-Origin': '*',
            },  
        }

    try:
        if 'doDeleteOrder' in req and req['doDeleteOrder']:
            delete_order(table, req)
        else:
            add_or_insert(table, req)
    except Exception as e:
        return {
           'statusCode': 500,
            'body': f'Error Occured: {e}',
            'headers': {
                'Access-Control-Allow-Origin': '*',
            },
        }
        
    return {
        'statusCode': 200,
        'body': json.dumps('Order Entered!'),
        'headers': {
            'Access-Control-Allow-Origin': '*',
        },
    }
