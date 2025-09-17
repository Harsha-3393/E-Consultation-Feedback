import pandas as pd
import re

print("--- Step 1: Loading and Merging Data ---")

try:
    reviews_df = pd.read_csv('ecom_reviews.csv')
    products_df = pd.read_csv('product_data.csv')
    context_df = pd.read_csv('context.csv')
    print("Datasets loaded successfully.")
except FileNotFoundError:
    print("One or more raw CSV files not found. Please create them first.")
    exit()

merged_df = pd.merge(reviews_df, products_df, on='product_id', how='left')
merged_df = pd.merge(merged_df, context_df, on='city', how='left')

merged_df['date'] = pd.to_datetime(merged_df['date'])

print("\nMerged DataFrame Head:")
print(merged_df.head())
print("\nMerged DataFrame Info:")
print(merged_df.info())

print("\n--- Step 2: Data Cleaning and Pre-processing ---")

merged_df['is_monsoon'].fillna(False, inplace=True)
merged_df['is_festival'].fillna(False, inplace=True)
print("Missing values handled.")

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = re.sub('<.*?>', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = text.lower()
    return text

merged_df['cleaned_review'] = merged_df['review_text'].apply(clean_text)

print("\nCleaned Reviews:")
print(merged_df[['review_text', 'cleaned_review']].head())

merged_df.to_csv('preprocessed_ecom_data.csv', index=False)
print("\nPreprocessed data saved to preprocessed_ecom_data.csv")