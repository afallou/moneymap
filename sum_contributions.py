import json

if __name__ == "__main__":
    sum = 0
    with open('contributions.json') as c:
        contributions = json.load(c)
        for recipient in contributions:
            for contribution in recipient["contributors"]:
                sum += float(contribution["amount"])
    print '%e' % sum