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
def prob(delta, coef):
    return decimal.Decimal(1.0 / (1.0 + (math.pow(10.0, float(delta) / (400.0 * coef)))))

States = ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"]
#i think it's probably possible to remove this and instead select from DB, might be a way to attempt to save memory though unsure
Drinks = ["7UP", "Coke", "Coke Zero", "Crush", "Diet Coke", "Dr. Pepper", "Fanta", "Ginger Ale", "Hi-C", "Icee", "Izze", "Monster Energy", "Mountain Dew", "Pepsi", "Red Bull", "Shirley Temple", "Sierra Mist", "Slurpee", "Sparkling Water", "Sprite", "Sunkist", "Almond Milk", "Apple Juice", "Caprisun", "Coffee", "Cranberry Juice", "Fruit Punch", "Gatorade", "Ginger Tea", "Grape Juice", "Green Tea", "Hot Chocolate", "Kool-Aid", "Lemonade", "Mango Juice", "Milk", "Milk Tea", "Orange Juice", "Pineapple Juice", "Powerade", "Root Beer", "Soy Milk", "Tomato Juice", "Water", "Watermelon Juice", "Yakult"]
Junkfood= ["Airheads", "Almond Joy", "Altoids", "Baby Ruth", "Butterfinger", "Candy Corn", "Caramel Apple Pop", "Chips Ahoy", "Chex Mix", "Cotton Candy", "Dum Dums", "Ferrero Rocher", "Fruit by the Foot", "Gobstoppers", "Gummy Worms", "Haribo Gold Bears", "Hershey's", "Hershey's Kisses", "Hi-Chew", "Icebreakers", "Jelly Belly", "Jolly Rancher", "Kit Kat", "Life Savers", "Lindt", "M&M", "Mars Bar", "Mentos", "Milano Cookie", "Milky Way", "Nerds", "Nestle Crunch", "Nilla Wafer", "Nutella", "Oreo", "Otter Pop", "Payday", "Pocky", "Red Vines", "Reese's Peanut Butter Cups", "Reese's Pieces", "Roshen", "Skittles", "Smarties", "Snickers", "Sour Patch", "Starbursts", "Swedish Fish", "Teddy Grahams", "Three Musketeers", "Tic Tacs", "Toblerone", "Tootsie Roll", "Twix", "Twizzlers", "Whoppers Malt Balls", "Welch's Fruit Snacks", "Werther's Original", "Yanyan", "Bubblegum Ice Cream", "Burnt Caramel Ice Cream", "Butter Pecan Ice Cream", "Cake Batter Ice Cream", "Cookie Dough Ice Cream", "Cookies and Cream Ice Cream", "Cotton Candy Ice Cream", "Dark Chocolate Ice Cream", "Green Tea Ice Cream", "Mint Chocolate Chip Ice Cream", "Neapolitan Ice Cream", "Pistachio Ice Cream", "Rocky Road Ice Cream", "Strawberry Ice Cream", "Vanilla Ice Cream", "Wasabi Ice Cream", "Cheetos", "Cheez-its", "Doritos", "Fritos", "Goldfish", "Kettle Brand", "Lays Original", "Lays Sour Cream & Onion", "Nutter Butter", "Pita Chips", "Pringles", "Ritz", "Ruffles", "Sun Chips", "Tostitos", "Wheat Thins"]
Maths = ["IMO 2010/1", "IMO 2010/2", "IMO 2010/3", "IMO 2010/4", "IMO 2010/5", "IMO 2010/6", "IMO 2011/1", "IMO 2011/2", "IMO 2011/3", "IMO 2011/4", "IMO 2011/5", "IMO 2011/6", "IMO 2012/1", "IMO 2012/2", "IMO 2012/3", "IMO 2012/4", "IMO 2012/5", "IMO 2012/6", "IMO 2013/1", "IMO 2013/2", "IMO 2013/3", "IMO 2013/4", "IMO 2013/5", "IMO 2013/6", "IMO 2014/1", "IMO 2014/2", "IMO 2014/3", "IMO 2014/4", "IMO 2014/5", "IMO 2014/6", "IMO 2015/1", "IMO 2015/2", "IMO 2015/3", "IMO 2015/4", "IMO 2015/5", "IMO 2015/6", "IMO 2016/1", "IMO 2016/2", "IMO 2016/3", "IMO 2016/4", "IMO 2016/5", "IMO 2016/6", "IMO 2017/1", "IMO 2017/2", "IMO 2017/3", "IMO 2017/4", "IMO 2017/5", "IMO 2017/6", "IMO 2018/1", "IMO 2018/2", "IMO 2018/3", "IMO 2018/4", "IMO 2018/5", "IMO 2018/6", "IMO 2019/1", "IMO 2019/2", "IMO 2019/3", "IMO 2019/4", "IMO 2019/5", "IMO 2019/6", "IMO 2020/1", "IMO 2020/2", "IMO 2020/3", "IMO 2020/4", "IMO 2020/5", "IMO 2020/6", "USA TSTST 2014/1", "USA TSTST 2014/2", "USA TSTST 2014/3", "USA TSTST 2014/4", "USA TSTST 2014/5", "USA TSTST 2014/6", "USA TSTST 2015/1", "USA TSTST 2015/2", "USA TSTST 2015/3", "USA TSTST 2015/4", "USA TSTST 2015/5", "USA TSTST 2015/6", "USA TSTST 2016/1", "USA TSTST 2016/2", "USA TSTST 2016/3", "USA TSTST 2016/4", "USA TSTST 2016/5", "USA TSTST 2016/6", "USA TSTST 2017/1", "USA TSTST 2017/2", "USA TSTST 2017/3", "USA TSTST 2017/4", "USA TSTST 2017/5", "USA TSTST 2017/6", "USA TSTST 2018/1", "USA TSTST 2018/2", "USA TSTST 2018/3", "USA TSTST 2018/4", "USA TSTST 2018/5", "USA TSTST 2018/6", "USA TSTST 2018/7", "USA TSTST 2018/8", "USA TSTST 2018/9", "USA TSTST 2019/1", "USA TSTST 2019/2", "USA TSTST 2019/3", "USA TSTST 2019/4", "USA TSTST 2019/5", "USA TSTST 2019/6", "USA TSTST 2019/7", "USA TSTST 2019/8", "USA TSTST 2019/9", "USA TSTST 2020/1", "USA TSTST 2020/2", "USA TSTST 2020/3", "USA TSTST 2020/4", "USA TSTST 2020/5", "USA TSTST 2020/6", "USA TSTST 2020/7", "USA TSTST 2020/8", "USA TSTST 2020/9", "USAMO 2010/1", "USAMO 2010/2", "USAMO 2010/3", "USAMO 2010/4", "USAMO 2010/5", "USAMO 2010/6", "USAMO 2011/1", "USAMO 2011/2", "USAMO 2011/3", "USAMO 2011/4", "USAMO 2011/5", "USAMO 2011/6", "USAMO 2012/1", "USAMO 2012/2", "USAMO 2012/3", "USAMO 2012/4", "USAMO 2012/5", "USAMO 2012/6", "USAMO 2013/1", "USAMO 2013/2", "USAMO 2013/3", "USAMO 2013/4", "USAMO 2013/5", "USAMO 2013/6", "USAMO 2014/1", "USAMO 2014/2", "USAMO 2014/3", "USAMO 2014/4", "USAMO 2014/5", "USAMO 2014/6", "USAMO 2015/1", "USAMO 2015/2", "USAMO 2015/3", "USAMO 2015/4", "USAMO 2015/5", "USAMO 2015/6", "USAMO 2016/1", "USAMO 2016/2", "USAMO 2016/3", "USAMO 2016/4", "USAMO 2016/5", "USAMO 2016/6", "USAMO 2017/1", "USAMO 2017/2", "USAMO 2017/3", "USAMO 2017/4", "USAMO 2017/5", "USAMO 2017/6", "USAMO 2018/1", "USAMO 2018/2", "USAMO 2018/3", "USAMO 2018/4", "USAMO 2018/5", "USAMO 2018/6", "USAMO 2019/1", "USAMO 2019/2", "USAMO 2019/3", "USAMO 2019/4", "USAMO 2019/5", "USAMO 2019/6", "USAMO 2020/1", "USAMO 2020/2", "USAMO 2020/3", "USAMO 2020/4", "USAMO 2020/5", "USAMO 2020/6", "USAMO 2021/1", "USAMO 2021/2", "USAMO 2021/3", "USAMO 2021/4", "USAMO 2021/5", "USAMO 2021/6", "USA TST 2014/1", "USA TST 2014/2", "USA TST 2014/3", "USA TST 2014/4", "USA TST 2014/5", "USA TST 2014/6", "USA TST 2015/1", "USA TST 2015/2", "USA TST 2015/3", "USA TST 2015/4", "USA TST 2015/5", "USA TST 2015/6", "USA TST 2016/1", "USA TST 2016/2", "USA TST 2016/3", "USA TST 2016/4", "USA TST 2016/5", "USA TST 2016/6", "USA TST 2017/1", "USA TST 2017/2", "USA TST 2017/3", "USA TST 2017/4", "USA TST 2017/5", "USA TST 2017/6", "USA TST 2018/1", "USA TST 2018/2", "USA TST 2018/3", "USA TST 2018/4", "USA TST 2018/5", "USA TST 2018/6", "USA TST 2019/1", "USA TST 2019/2", "USA TST 2019/3", "USA TST 2019/4", "USA TST 2019/5", "USA TST 2019/6", "USA TST 2020/1", "USA TST 2020/2", "USA TST 2020/3", "USA TST 2020/4", "USA TST 2020/5", "USA TST 2020/6"]
# Shortlist = ["Shortlist 2009/A2", "Shortlist 2010/A3", "Shortlist 2010/A4", "Shortlist 2010/A5", "Shortlist 2010/A6", "Shortlist 2010/A8", "Shortlist 2010/C1", "Shortlist 2010/C2", "Shortlist 2010/C3", "Shortlist 2010/C5", "Shortlist 2010/C6", "Shortlist 2010/C7", "Shortlist 2010/G1", "Shortlist 2010/G3", "Shortlist 2010/G5", "Shortlist 2010/G6", "Shortlist 2010/G7", "Shortlist 2010/N1", "Shortlist 2010/N2", "Shortlist 2010/N3", "Shortlist 2010/N4", "Shortlist 2010/N6", "Shortlist 2011/A2", "Shortlist 2011/A3", "Shortlist 2011/A4", "Shortlist 2011/A5", "Shortlist 2011/A7", "Shortlist 2011/C2", "Shortlist 2011/C4", "Shortlist 2011/C5", "Shortlist 2011/C6", "Shortlist 2011/C7", "Shortlist 2011/G1", "Shortlist 2011/G2", "Shortlist 2011/G3", "Shortlist 2011/G4", "Shortlist 2011/G5", "Shortlist 2011/G6", "Shortlist 2011/G7", "Shortlist 2011/N1", "Shortlist 2011/N2", "Shortlist 2011/N3", "Shortlist 2011/N4", "Shortlist 2011/N6", "Shortlist 2011/N7", "Shortlist 2011/N8", "Shortlist 2012/A2", "Shortlist 2012/A4", "Shortlist 2012/A5", "Shortlist 2012/A6", "Shortlist 2012/A7", "Shortlist 2012/C1", "Shortlist 2012/C2", "Shortlist 2012/C3", "Shortlist 2012/C4", "Shortlist 2012/C5", "Shortlist 2012/C7", "Shortlist 2012/G2", "Shortlist 2012/G3", "Shortlist 2012/G4", "Shortlist 2012/G6", "Shortlist 2012/G7", "Shortlist 2012/G8", "Shortlist 2012/N1", "Shortlist 2012/N2", "Shortlist 2012/N3", "Shortlist 2012/N4", "Shortlist 2012/N5", "Shortlist 2012/N6", "Shortlist 2012/N8", "Shortlist 2013/A1", "Shortlist 2013/A2", "Shortlist 2013/A4", "Shortlist 2013/A5", "Shortlist 2013/A6", "Shortlist 2013/C1", "Shortlist 2013/C3", "Shortlist 2013/C4", "Shortlist 2013/C5", "Shortlist 2013/C6", "Shortlist 2013/C8", "Shortlist 2013/G2", "Shortlist 2013/G3", "Shortlist 2013/G4", "Shortlist 2013/G5", "Shortlist 2013/N1", "Shortlist 2013/N3", "Shortlist 2013/N4", "Shortlist 2013/N5", "Shortlist 2013/N6", "Shortlist 2013/N7", "Shortlist 2014/A2", "Shortlist 2014/A3", "Shortlist 2014/A4", "Shortlist 2014/A5", "Shortlist 2014/A6", "Shortlist 2014/C1", "Shortlist 2014/C2", "Shortlist 2014/C4", "Shortlist 2014/C6", "Shortlist 2014/C7", "Shortlist 2014/C8", "Shortlist 2014/C9", "Shortlist 2014/G2", "Shortlist 2014/G3", "Shortlist 2014/G4", "Shortlist 2014/G6", "Shortlist 2014/G7", "Shortlist 2014/N1", "Shortlist 2014/N2", "Shortlist 2014/N4", "Shortlist 2014/N5", "Shortlist 2014/N6", "Shortlist 2014/N7", "Shortlist 2014/N8", "Shortlist 2015/A1", "Shortlist 2015/A2", "Shortlist 2015/A3", "Shortlist 2015/A5", "Shortlist 2015/A6", "Shortlist 2015/C1", "Shortlist 2015/C3", "Shortlist 2015/C4", "Shortlist 2015/C6", "Shortlist 2015/C7", "Shortlist 2015/G1", "Shortlist 2015/G3", "Shortlist 2015/G4", "Shortlist 2015/G5", "Shortlist 2015/G7", "Shortlist 2015/G8", "Shortlist 2015/N1", "Shortlist 2015/N2", "Shortlist 2015/N3", "Shortlist 2015/N4", "Shortlist 2015/N6", "Shortlist 2015/N7", "Shortlist 2015/N8", "Shortlist 2016/A1", "Shortlist 2016/A2", "Shortlist 2016/A3", "Shortlist 2016/A4", "Shortlist 2016/A5", "Shortlist 2016/A7", "Shortlist 2016/A8", "Shortlist 2016/C1", "Shortlist 2016/C2", "Shortlist 2016/C3", "Shortlist 2016/C5", "Shortlist 2016/C6", "Shortlist 2016/C8", "Shortlist 2016/G2", "Shortlist 2016/G3", "Shortlist 2016/G4", "Shortlist 2016/G5", "Shortlist 2016/G6", "Shortlist 2016/G7", "Shortlist 2016/G8", "Shortlist 2016/N1", "Shortlist 2016/N2", "Shortlist 2016/N4", "Shortlist 2016/N5", "Shortlist 2016/N6", "Shortlist 2016/N8", "Shortlist 2017/A1", "Shortlist 2017/A2", "Shortlist 2017/A3", "Shortlist 2017/A4", "Shortlist 2017/A5", "Shortlist 2017/A7", "Shortlist 2017/A8", "Shortlist 2017/C1", "Shortlist 2017/C2", "Shortlist 2017/C3", "Shortlist 2017/C6", "Shortlist 2017/C7", "Shortlist 2017/C8", "Shortlist 2017/G1", "Shortlist 2017/G3", "Shortlist 2017/G4", "Shortlist 2017/G5", "Shortlist 2017/G6", "Shortlist 2017/G7", "Shortlist 2017/G8", "Shortlist 2017/N2", "Shortlist 2017/N3", "Shortlist 2017/N4", "Shortlist 2017/N5", "Shortlist 2017/N6", "Shortlist 2017/N8", "Shortlist 2018/A1", "Shortlist 2018/A3", "Shortlist 2018/A4", "Shortlist 2018/A5", "Shortlist 2018/A6", "Shortlist 2018/A7", "Shortlist 2018/C1", "Shortlist 2018/C3", "Shortlist 2018/C5", "Shortlist 2018/C6", "Shortlist 2018/C7", "Shortlist 2018/G2", "Shortlist 2018/G3", "Shortlist 2018/G4", "Shortlist 2018/G5", "Shortlist 2018/G7", "Shortlist 2018/N1", "Shortlist 2018/N2", "Shortlist 2018/N3", "Shortlist 2018/N5", "Shortlist 2018/N6", "Shortlist 2018/N7", "Shortlist 2019/A2", "Shortlist 2019/A3", "Shortlist 2019/A4", "Shortlist 2019/A5", "Shortlist 2019/A6", "Shortlist 2019/A7", "Shortlist 2019/C1", "Shortlist 2019/C2", "Shortlist 2019/C4", "Shortlist 2019/C6", "Shortlist 2019/C7", "Shortlist 2019/C8", "Shortlist 2019/C9", "Shortlist 2019/G1", "Shortlist 2019/G2", "Shortlist 2019/G4", "Shortlist 2019/G5", "Shortlist 2019/G6", "Shortlist 2019/G8", "Shortlist 2019/N2", "Shortlist 2019/N3", "Shortlist 2019/N4", "Shortlist 2019/N5", "Shortlist 2019/N6", "Shortlist 2019/N7", "Shortlist 2019/N8"]
Nfl = ["Arizona Cardinals", "Atlanta Falcons", "Baltimore Ravens", "Buffalo Bills", "Carolina Panthers", "Chicago Bears", "Cincinnati Bengals", "Cleveland Browns", "Dallas Cowboys", "Denver Broncos", "Detroit Lions", "Green Bay Packers", "Houston Texans", "Indianapolis Colts", "Jacksonville Jaguars", "Kansas City Chiefs", "Las Vegas Raiders", "Los Angeles Chargers", "Los Angeles Rams", "Miami Dolphins", "Minnesota Vikings", "New England Patriots", "New Orleans Saints", "New York Giants", "New York Jets", "Philadelphia Eagles", "Pittsburgh Steelers", "San Francisco 49ers", "Seattle Seahawks", "Tampa Bay Buccaneers", "Tennessee Titans", "Washington Football Team"]
Nba = ["Atlanta Hawks", "Boston Celtics", "Brooklyn Nets", "Charlotte Hornets", "Chicago Bulls", "Cleveland Cavaliers", "Dallas Mavericks", "Denver Nuggets", "Detroit Pistons", "Golden State Warriors", "Houston Rockets", "Indiana Pacers", "Los Angeles Clippers", "Los Angeles Lakers", "Memphis Grizzlies", "Miami Heat", "Milwaukee Bucks", "Minnesota Timberwolves", "New Orleans Pelicans", "New York Knicks", "Oklahoma City Thunder", "Orlando Magic", "Philadelphia 76ers", "Phoenix Suns", "Portland Trail Blazers", "Sacramento Kings", "San Antonio Spurs", "Toronto Raptors", "Utah Jazz", "Washington Wizards"]
Hiphop = ["Drake", "Jay-Z", "Kanye West", "Eminem", "Lil Wayne", "Kendrick Lamar", "Nas", "Tupac Shakur", "The Notorious B.I.G.", "Snoop Dogg", "Dr. Dre", "Nicki Minaj", "50 Cent", "Travis Scott", "Ice Cube", "OutKast", "J. Cole", "Future", "Young Thug", "Wu-Tang Clan", "Migos", "Cardi B.", "T.I.", "Lil Uzi Vert", "Public Enemy", "Diddy", "Gucci Mane", "Rick Ross", "Busta Rhymes", "Meek Mill", "Big Sean", "LL Cool J", "Run-D.M.C.", "Beastie Boys", "A Tribe Called Quest", "Post Malone", "21 Savage", "Lauryn Hill", "André 3000", "Juice WRLD", "Beyoncé", "Rakim", "Lil Baby", "Chance the Rapper", "Missy Elliott", "DMX", "Method Man", "Ludacris", "Eazy-E", "Kid Cudi", "Lil Tjay", "Polo G", "XXXTentacion", "The Kid Laroi", "The Weeknd", "6LACK", "24kGoldn", "DaBaby", "Jack Harlow", "Lil Mosey", "Joyner Lucas", "Pop Smoke", "NLE Choppa", "Trippie Redd", "NF", "Roddy Ricch", "Playboi Carti", "Tory Lanez", "Chris Brown", "Lil Durk", "YoungBoy Never Broke Again", "Mac Miller", "Logic", "G-Eazy"]
Classical = ["Beethoven", "Mozart", "J.S. Bach", "Chopin", "Brahms", "Handel", "Debussy", "Vivaldi", "Haydn", "Schubert", "Liszt", "Verdi", "Schumann", "Mendelssohn", "Mahler", "Stravinsky", "Wagner", "Rachmaninoff", "Dvorak", "Shostakovich", "Elgar", "Strauss", "Bernstein", "Ravel", "Prokofiev", "Vaughan Williams", "Bartok", "Puccini", "Holst", "Schoenberg", "Grieg", "Britten", "Saint-Saens", "Gershwin", "Copland", "Berlioz", "Tchaikovsky", "Sibelius", "Paganini", "Boccherini", "Bizet", "Telemann", "Scarlatti", "Morricone", "Borodin", "Czerny", "Bruckner", "Satie", "Berg", "Barber"]

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

def valid(table, name):
    res = table.query(
        ProjectionExpression="#nm, Rating",
        ExpressionAttributeNames={"#nm": "Name"},
        KeyConditionExpression=Key('Name').eq(name))
    return True if res['Items'] else False

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
        ok = valid(table, winner) and valid(table, loser)
        coef = 1.0
        if (dbname == "States"):
            res1, res2 = select_items(States)
            coef = 2.0
        if (dbname == "Drinks"):
            res1, res2 = select_items(Drinks)
        if (dbname == "Junkfood"):
            res1, res2 = select_items(Junkfood)
        if (dbname == "Maths"):
            res1, res2 = select_items(Maths)
        if (dbname == "Nfl"):
            res1, res2 = select_items(Nfl)
            coef = 2.0
        if (dbname == "Nba"):
            res1, res2 = select_items(Nba)
            coef = 2.0
        if (dbname == "Hiphop"):
            res1, res2 = select_items(Hiphop)
        if (dbname == "Classical"):
            res1, res2 = select_items(Classical)
        if winner in keywords or ok == False:
            return response(json.dumps({"choice1": res1, "choice2": res2}), 200)
        winner_rtg = get_item(table, winner)['Rating']
        loser_rtg = get_item(table, loser)['Rating']
        p = prob(winner_rtg - loser_rtg, coef) #1-probability of what happened
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
