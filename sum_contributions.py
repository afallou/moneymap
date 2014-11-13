import json
from collections import Counter

if __name__ == "__main__":
    total_sum = 0
    reasons = Counter()
    reason_sums = Counter()

    with open('contributions.json') as c:
        contributions = json.load(c)
        for recipient in contributions:
            # Obama: 400629
            # Biden: 300008
            if recipient["recipient_id"] != 400629 and recipient["recipient_id"] != 300008:
                for contribution in recipient["contributors"]:
                    total_sum += float(contribution["amount"])
                    reasons[contribution["transaction_type_description"]] += 1
                    reason_sums[contribution["transaction_type_description"]] += float(contribution["amount"])

    print 'Total sum: %e' % total_sum
    print "Total count:", sum(reasons.values())
    print "Breakdown count", reasons
    print "Breakdown sums", reason_sums