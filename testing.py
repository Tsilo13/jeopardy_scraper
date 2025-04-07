import pandas as pd 

clues_df = pd.read_csv('data/csv/clues.csv')
for col in ['value', 'clue_text', 'correct_response']:
    clues_df[col] = clues_df[col].fillna('').astype(str).str.strip()
clues_data = clues_df.to_dict(orient='records')

#duplicates = clues_df[clues_df.duplicated(subset='clue_id', keep=False)]
#print(duplicates[['clue_id']])

#dupes = clues_df.groupby(['category_id', 'value']).size()
#print(dupes[dupes > 1])

#for testing string length
#max(clues_df['value'].astype(str).str.len())
"""
for record in clues_df:
    if not isinstance(record['value'], str) or \
       not isinstance(record['clue_text'], str) or \
       not isinstance(record['correct_response'], str):
        print("Bad record:", record)
        break
"""

for i, record in enumerate(clues_data ):
    if not isinstance(record, dict):
        print(f"Bad record at index {i}: not a dict →", record)
        continue  # skip to next one
    for key in ['value', 'clue_text', 'correct_response']:
        if not isinstance(record[key], str):
            print(f"Bad value at row {i}, column '{key}':", record[key], type(record[key]))


