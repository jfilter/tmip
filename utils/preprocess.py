# The preprocessing steps all in one

import logging
import math
import os

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

# Input:
PATH_ARTICLES = '/mnt/data/datasets/newspapers/guardian/articles.csv'
PATH_ORIG_COMMENTS = '/mnt/data/datasets/newspapers/guardian/comments.csv'
PATH_TOKENIZED_TEXT = '/mnt/data/datasets/newspapers/guardian/sorted_comments_twokenized_lower'

# Output:
PATH_MERGED_COMMENTS = '/mnt/data/group07/johannes/proc_data/merged_comments.csv'

AMOUNT_OF_RANKS = 10

logger = logging.getLogger(__name__)

def process_tokenized_text():
    logger.info('Reading original comments data')
    comments = pd.read_csv(PATH_ORIG_COMMENTS, usecols=lambda x: x != 'comment_text')

    logger.info('Reading tokenized text')
    text = pd.read_table(PATH_TOKENIZED_TEXT, skip_blank_lines=False)

    assert comments.shape[0] == text.shape[0]

    logger.info('Merging tokenized text into comment data')
    comments = pd.concat([comments, text], axis=1)
    del text  # free memory
    comments.rename(inplace=True, index=str, columns={"commen t_t ext": "comment_text"})  # the tokenized file has a strange col name
    
    comments.to_csv(PATH_MERGED_COMMENTS)


def filter_comments_by_category(category='sport'):  # "politics"
    # Output:
    path_category_comments = f"/mnt/data/group07/johannes/proc_data/{category}_comments.csv"
    
    logger.info('Collecting articles')
    articles = pd.read_csv(PATH_ARTICLES)
    articles = articles[articles['article_url'].str.contains("https://www.theguardian.com/" + category + "/")]

    # Read in chunkwise
    chunksize = 10 ** 6
    comments_list = []

    logger.info('Reading merged comments chunkwise')
    for chunk in pd.read_csv(PATH_MERGED_COMMENTS, chunksize=chunksize):
        comment_chunk = chunk[chunk['comment_text'].notnull()]  # filter out NaNs
        comment_chunk = comment_chunk[comment_chunk['parent_comment_id'].isnull()]  # only select root comments
        comment_chunk = comment_chunk[comment_chunk['article_id'].isin(articles['article_id'])]  # filter out article in category
        comment_chunk = comment_chunk.drop(['parent_comment_id'], axis=1)
        comments_list.append(comment_chunk)

    # it's faster to first gather all in a list and concat once
    comments = pd.concat(comments_list)
    
    logger.info('Storing filtered category comments')
    comments.to_csv(path_category_comments)
    
    return path_category_comments


def _enhance_and_filter_comments(co):
    logger.info('Enhance comments with rank and apply filtering')
    groupby = co.groupby('article_id')
    co['rank'] = groupby['timestamp'].rank(method='dense').astype(int)
    co = co[co['rank'] <= AMOUNT_OF_RANKS]  # select only first 10 comments
    co['total_upvotes'] = groupby['upvotes'].transform('sum')
    co['total_comments'] = groupby['upvotes'].transform('count')
    co = co[co['total_upvotes'] > 20]  # do not consider articles with under 10 upvotes
    co = co[co['total_comments'] == 10]  # remove articles with over under 10 comments. 
    co['rel_upvotes'] = co.apply(lambda row: (row.upvotes / row.total_upvotes) * 100, axis=1)
    return co


def _split_and_label(enhanced_comments, top_bot_perc):
    logger.info(f'Label data for perc {top_bot_perc}')
    
    num_rows = co.shape[0]
    N = int((num_rows * top_bot_perc) / AMOUNT_OF_RANKS)
    groupby = co.groupby("rank", group_keys=False)
    
    res_pos = groupby.apply(lambda g: g.nlargest(N, "rel_upvotes", keep="last"))
    res_pos['class'] = 1
    
    res_neg = groupby.apply(lambda g: g.nsmallest(N, "rel_upvotes", keep="first"))
    if (top_bot_perc == 0.5):
        # There is a problem when the want to bin the *whole* dataset. It would result in 2 duplicates. Most likely due to 
        # rel_upvotes is the same for multiple values and it's not possible to have a clear cut.
        res = pd.merge(co, res_pos, how='left')
        res['class'] = res['class'].fillna(0)
    else:
        res_neg['class'] = 0
        res = pd.concat([res_pos, res_neg])

    assert(res[res['class'] == 0].shape[0] == res[res['class'] == 1].shape[0])  # ensure same number of classes
    assert(res['comment_id'].is_unique)  # make sure we don't have duplicates
    return res


def filter_by_rank(path_category_comments, category='politics', suffix='_fixed'):
    co = pd.read_csv(path_category_comments)
    co = _enhance_and_filter_comments(co)
    for top_bot_perc in [0.1, 0.25, 0.5]:
        co = _split_and_label(co, top_bot_perc)
        co.to_csv(f"/mnt/data/group07/johannes/proc_data/classes_{category}_comments_{top_bot_perc}{suffix}.csv")


def split_train_val_test(category='politics', suffix='_fixed'):
    perc = ['0.1', '0.25', '0.5']

    for p in perc:
        logger.info(f'Create train, val and test set for category {category} and perc {p}')
        outdir = f'/mnt/data/group07/johannes/exp_data/{category}_{p}{suffix}'
        if not os.path.exists(outdir):
            os.mkdir(outdir)

        df = pd.read_csv(f'/mnt/data/group07/johannes/proc_data/classes_{category}_comments_{p}{suffix}.csv')
        train, not_train = train_test_split(df, test_size=0.2)  # first train: 0.8
        val, test = train_test_split(not_train, test_size=0.5)  # then, val: 0.1, test: 0.1
        
        train.to_csv(outdir + '/train.csv')
        val.to_csv(outdir + '/val.csv')
        test.to_csv(outdir + '/test.csv')


if __name__ == "__main__":
    merged_path = process_tokenized_text()

    path = filter_comments_by_category(merged_path, category='sport')
    filter_by_rank(path, category='sport', suffix='_new')
    split_train_val_test(category='sport', suffix='_new')

    path = filter_comments_by_category(merged_path, category='politics')
    filter_by_rank(path, category='politics', suffix='_new')
    split_train_val_test(category='politics', suffix='_new')
