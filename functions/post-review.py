#
#
# main() will be run when you invoke this action
#
# @param Cloud Functions actions accept a single parameter, which must be a JSON object.
#
# @return The output of this action, which must be a JSON object.
#
#
import sys

def main(dict):
    review = {}
    if 'review' in dict.keys():
        for key, value in dict['review'].items():
            review[key] = value

    return { 
        "doc":
            {
                "id": review.get('id', 123),
                "name": review.get('name', "Anonymous Reviewer"),
                "dealership": review.get('dealership', 1),
                "review": review.get('review', 'No review provided'),
                "purchase": review.get('purchase', False),
                "purchase_date": review.get('purchase_date', None),
                "car_make": review.get('car_make', None),
                "car_model": review.get('car_model', None),
                "car_year": review.get('car_year', None)
            }
    }