from typing import List
import pandas as pd


def create_recommedation(data: List[dict]) -> dict:
    df = pd.DataFrame(data)
    df['order_date'] = pd.to_datetime(df['order_date'])
    df['last_date'] = df.groupby('item_id')['order_date'].transform("max")
    df['first_date'] = df.groupby('item_id')['order_date'].transform("min")
    df['item_count'] = df.groupby('item_id')['item_id'].transform("size")
    df['frequency'] = ((df['last_date'] - df['first_date']).dt.days / df['item_count']).astype(int)
    df['from_last_order'] = ((pd.to_datetime('today') - df['last_date']).dt.days).astype(int)

    def calculate_recommendation(row):
        if row['from_last_order'] > row['frequency'] and row['frequency'] < 30 and (
                row['from_last_order'] - row['frequency']) < 20:
            return True
        elif row['frequency'] > 30 and row['from_last_order'] < 20:
            return True
        else:
            return False

    df['is_recommended'] = df.apply(calculate_recommendation, axis=1)
    df['last_date'] = pd.to_datetime(df['last_date'])
    selected_columns = ['item_id', 'item_name', 'price']
    return df[df['is_recommended'] == True][selected_columns].to_dict(orient='records')
