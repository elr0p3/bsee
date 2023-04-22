#!/usr/bin/python3

from dotenv import load_dotenv
import pandas as pd
import requests, os, argparse, json

# --- load environment variables ---
load_dotenv()
# API_KEY = os.getenv('API_KEY')

class BabelFy:
    def __init__(self):
        self.URL = 'https://babelfy.io/v1/disambiguate'
        self._api_key = os.getenv('API_KEY')

    def disambiguate(self, text: str, lang: str) -> list[dict]:
        params = {
            'text': text,
            'lang': lang,
            'key': self._api_key,
            # 'MCS': 'OFF',
        }
        r = requests.get(self.URL, params=params)
        return r.json()

    def obtain_id(self, response_json: list[dict], phrase: str, position: int) -> str:
        # print('-------------->', position)
        for token in response_json:
            # print(token['tokenFragment'])
            if token['tokenFragment']['start'] == position:
                return token['babelSynsetID']
        return ''


class Verifier:
    def __init__(self, df):
        self.total = len(df.index)
        self.success = 0

    def match_ids(self, human_id: str, babel_id: str):
        if human_id == babel_id:
            self.success += 1

    def __str__(self):
        return f'{self.success} / {self.total}'



if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Perform some text desambiguation through BabelFy API"
    )
    parser.add_argument('--csv', help='Input CSV file to retreive phrases', required=True)
    args = vars(parser.parse_args())

    df = pd.read_csv(args['csv'], sep=';')
    verifier = Verifier(df)
    babelfy = BabelFy()

    for i, row in df.iterrows():
        response_json = babelfy.disambiguate(
            str(row['phrases']),
            str(row['language'])
        )
        babel_id = babelfy.obtain_id(
            response_json,
            str(row['phrases']),
            int(row['position'])
        )
        verifier.match_ids(
            str(row['ID']),
            babel_id
        )

    print(verifier)
