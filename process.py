import json
import random
import math
import boto3
import decimal
from boto3.dynamodb.conditions import Key

kfactor = decimal.Decimal(20.0)
default_rtg = decimal.Decimal(1500.0)
keywords = ["Start", "Loading", "..."]

# probability x wins against x + delta
def prob(delta):
    return decimal.Decimal(1.0 / (1.0 + (math.pow(10.0, float(delta) / (400.0)))))

States = ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"]
#i think it's probably possible to remove this and instead select from DB, might be a way to attempt to save memory though unsure
Drinks = ["7UP", "Coke", "Coke Zero", "Crush", "Diet Coke", "Dr. Pepper", "Fanta", "Ginger Ale", "Hi-C", "Icee", "Izze", "Monster Energy", "Mountain Dew", "Pepsi", "Red Bull", "Shirley Temple", "Sierra Mist", "Slurpee", "Sparkling Water", "Sprite", "Sunkist", "Almond Milk", "Apple Juice", "Caprisun", "Coffee", "Cranberry Juice", "Fruit Punch", "Gatorade", "Ginger Tea", "Grape Juice", "Green Tea", "Hot Chocolate", "Kool-Aid", "Lemonade", "Mango Juice", "Milk", "Milk Tea", "Orange Juice", "Pina Colada", "Pineapple Juice", "Powerade", "Root Beer", "Soy Milk", "Tomato Juice", "Water", "Watermelon Juice", "Yakult"]
Junkfood= ["Almond Joy", "Altoids", "Baby Ruth", "Butterfinger", "Candy Corn", "Ferrero Rocher", "Fruit by the Foot", "Gobstoppers", "Gummy Worms", "Haribo Gold Bears", "Hershey's", "Hershey's Kisses", "Hi-Chew", "Icebreakers", "Jelly Belly", "Jolly Rancher", "Kit Kat", "Lindt", "M&M", "Mars Bar", "Milano Cookie", "Milky Way", "Nerds", "Nestle Crunch", "Nilla Wafer", "Nutella", "Payday", "Pocky", "Reese's Peanut Butter Cups", "Reese's Pieces", "Roshen", "Skittles", "Smarties", "Snickers", "Starbursts", "Swedish Fish", "Three Musketeers", "Toblerone", "Twix", "Werther's Original", "Yanyan", "Bubblegum Ice Cream", "Burnt Caramel Ice Cream", "Butter Pecan Ice Cream", "Cake Batter Ice Cream", "Cookie Dough Ice Cream", "Cookies and Cream Ice Cream", "Dark Chocolate Ice Cream", "Green Tea Ice Cream", "Milk Chocolate Ice Cream", "Mint Chocolate Chip Ice Cream", "Neapolitan Ice Cream", "Pistachio Ice Cream", "Rocky Road Ice Cream", "Strawberry Ice Cream", "Vanilla Ice Cream", "Wasabi Ice Cream", "Cheetos", "Cheez-its", "Doritos", "Fritos", "Goldfish", "Kettle Brand", "Lays Original", "Nutter Butter", "Pita Chips", "Pringles", "Ritz", "Ruffles", "Sun Chips", "Tostitos", "Wheat Thins"]

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
    if (requestid == 0): #someone wins against someone else
        winner = data["winner"]
        loser = data["loser"]
        res1 = ""
        res2 = ""
        if (dbname == "States"):
            res1, res2 = select_items(States)
        if (dbname == "Drinks"):
            res1, res2 = select_items(Drinks)
        if (dbname == "Junkfood"):
            res1, res2 = select_items(Junkfood)
        if winner in keywords:
            return response(json.dumps({"choice1": res1, "choice2": res2}), 200)
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
    if (requestid == 1): #requesting leaderboard
        stuff = table.scan()
        items = stuff['Items']
        items.sort(key = lambda cmp:-cmp["Rating"])
        for i in items:
            i["Rating"] = math.floor(i["Rating"])
            i["Wins"] = int(i["Wins"])
            i["Losses"] = int(i["Losses"])
        items = [x for x in items if not x["Name"] in keywords]
        return response(json.dumps(items), 200)
