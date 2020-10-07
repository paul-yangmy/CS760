import requests
import json
import pandas as pd
from time import sleep


def steamReviews(appId, numOfSets, reviewType):
    '''
        Return a dataframe of steam app reviews and other data

        appId(str): unique id for apps on steam
        numOfSets(int): number of sets (20 reviews in a set here) of reviews
        reviewType(int): 0 for nagetive, 1 for positive, 2 for all
    '''
    url = 'https://store.steampowered.com/appreviews/' + appId + '?json=1'
    payload = {
        'filter': 'all',  # sort by helpfulness
        'language': 'english',
        # english reviews only (there's a language differentiation problem of steam when sort by helpfulness)
        'cursor': '*',  # pass * for the first set
        'review_type': 'all',  # positive and negative ones
        'num_perpage': '100'  # num of reviews to be returned (could be up to 100)
    }
    if reviewType == 0:
        payload['review_type'] = 'negative'
    elif reviewType == 1:
        payload['review_type'] = 'positive'
    else:
        pass
    cursor = '*'
    allVotes = []
    allHelpfulness = []
    allPlaytime = []
    allReviews = []
    allId = []
    allWeighted = []
    for i in range(1, numOfSets + 1):
        print("collecting " + str(i) + "th set...")
        payload['cursor'] = cursor
        reviewsJson = json.loads(requests.get(url, params=payload).text)
        # extract response variables
        success = reviewsJson['success']  # 1 if the query was successful
        if success == False:
            raise Exception('Query failed')
        cursor = reviewsJson[
            'cursor']  # The value to pass into the next request as the cursor to retrieve the next batch of reviews
        reviews = reviewsJson['reviews']  # set of reviews

        # iterating 100 reviews in a set
        for j in range(0, len(reviews)):
            review = reviews[j]
            allVotes.append(review['voted_up'])  # true for recommendation
            allHelpfulness.append(review['votes_up'])  # num of users found it helpful
            allPlaytime.append(review['author']['playtime_forever'])  # lifetime playtime of the author
            allReviews.append(review['review'])  # text of review
            allWeighted.append(review['weighted_vote_score'])
            allId.append(review['author']['steamid'])

        # # control request frequency
        # if (i % 2 == 0) and (i != numOfSets):
        #     sleep(10)
        sleep(10)
    # output dataframe
    steamDf = pd.DataFrame({
        'votes': allVotes,
        'helpfulness': allHelpfulness,
        'time': allPlaytime,
        'reviews': allReviews,
        'steamId': allId,
        'weighted_vote': allWeighted
    })
    return (steamDf)


rvData = steamReviews('374320', 20, 2)

rvData.to_csv("reviews.csv")
