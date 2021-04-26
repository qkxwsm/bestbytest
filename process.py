import json
import random
import math
import boto3
import decimal
from boto3.dynamodb.conditions import Key

kfactor = decimal.Decimal(20.0)
default_rtg = decimal.Decimal(1500.0)
initial = "Start"

# probability x wins against x + delta
def prob(delta):
    return decimal.Decimal(1.0 / (1.0 + (math.pow(10.0, float(delta) / (400.0)))))
    
States = ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"]
        
def response(message, status_code):
    return {
        'statusCode': str(status_code),
        'body': json.dumps(message),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            "Access-Control-Allow-Headers" : "Content-Type",
            "Access-Control-Allow-Methods": '*',
            "Access-Control-Allow-Credentials" : True
            },
        }
        
def upd_item(table, name, newrating, result):
    table.update_item(
        Key={"Name":name},
        UpdateExpression="SET Rating = :rating",
        ExpressionAttributeValues={":rating": newrating})
    if result == 0:
        table.update_item(
        Key={"Name":name},
        UpdateExpression="ADD #losses :increment",
        ExpressionAttributeNames={'#losses': 'Losses'},
        ExpressionAttributeValues={':increment': 1})
    if result == 1:
        table.update_item(
        Key={"Name":name},
        UpdateExpression="ADD #wins :increment",
        ExpressionAttributeNames={'#wins': 'Wins'},
        ExpressionAttributeValues={':increment': 1})
    if result == 2:
        table.update_item(
        Key={"Name":name},
        UpdateExpression="SET #wins = :zero, #losses = :zero",
        ExpressionAttributeNames={'#wins': 'Wins', '#losses': 'Losses'},
        ExpressionAttributeValues={':zero': 0})
    
def get_item(table, name):
    res = table.query(
        ProjectionExpression="#nm, Rating",
        ExpressionAttributeNames={"#nm": "Name"},
        KeyConditionExpression=Key('Name').eq(name))
    if not res['Items']:
        upd_item(table, name, default_rtg, 2)
        # table.put_item(Item={"Name":name,"Rating":default_rtg})
        res = table.query(
            ProjectionExpression="#nm, Rating",
            ExpressionAttributeNames={"#nm": "Name"},
            KeyConditionExpression=Key('Name').eq(name))
    return res['Items'][0]
    
def select_items(names):
    res1 = names[random.randint(0, len(names) - 1)]
    res2 = res1
    while(res2 == res1):
        res2 = names[random.randint(0, len(names) - 1)]
    return res1, res2
    
def lambda_handler(event, context):
    data = json.loads(event["body"])
    dbname = data["db"]
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(dbname)
    requestid=data["requestid"]
    if (requestid == 0):
        winner = data["winner"]
        loser = data["loser"]
        winner_rtg = get_item(table, winner)['Rating']
        loser_rtg = get_item(table, loser)['Rating']
        p = prob(winner_rtg - loser_rtg) #1-probability of what happened
        winner_delta = kfactor * p
        loser_delta = -kfactor * p
        winner_newrtg = winner_rtg + winner_delta
        loser_newrtg = loser_rtg + loser_delta
        upd_item(table, winner, winner_newrtg, 1)
        upd_item(table, loser, loser_newrtg, 0)
        winner_delta = math.floor(winner_newrtg) - math.floor(winner_rtg)
        loser_delta = math.floor(loser_newrtg) - math.floor(loser_rtg)
        res1 = ""
        res2 = ""
        if (dbname == "States"):
            res1, res2 = select_items(States)
        return response(json.dumps({
            "prob":1.0-float(p),
            "winner":winner,
            "winner_rtg":float(winner_newrtg),
            "winner_delta":winner_delta,
            "loser":loser,
            "loser_rtg":float(loser_newrtg), 
            "loser_delta":loser_delta,
            "choice1": res1,
            "choice2": res2}), 200)
    if (requestid == 1):
        stuff = table.scan()
        items = stuff['Items']
        items.sort(key = lambda cmp:-cmp["Rating"])
        for i in items:
            i["Rating"] = math.floor(i["Rating"])
            i["Wins"] = int(i["Wins"])
            i["Losses"] = int(i["Losses"])
        items = [x for x in items if x["Name"] != initial]
        return response(json.dumps(items), 200)
