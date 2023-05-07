#!/usr/bin/python3

from dotenv import load_dotenv
import pandas as pd
import requests, os, argparse
from functools import cache

# --- load environment variables ---
load_dotenv()

class BabelFyNet:
    def __init__(self):
        self.FY_URL = 'https://babelfy.io/v1/disambiguate'
        self.NET_URL = 'https://babelnet.io/v8/getSynset'
        self._api_key = os.getenv('API_KEY')

    def disambiguate(self, text: str, lang: str) -> list[dict]:
        params = {
            'text': text,
            'lang': lang,
            'key': self._api_key,
            # 'MCS': 'OFF',
        }
        r = requests.get(self.FY_URL, params=params)
        return r.json()

    def get_id_from_babelfy_response(self, response_json: list[dict], position: int) -> str:
        for token in response_json:
            if token['tokenFragment']['start'] == position:
                return token['babelSynsetID']
        return ''

    @cache
    def download_definition_from_synsetid(self, synset_id: str, lang: str) -> str:
        params = {
            'id': synset_id,
            'targetLang': lang,
            'key': self._api_key,
        }
        r = requests.get(self.NET_URL, params=params)
        try:
            definitions_data = r.json()['glosses']
            if len(definitions_data) > 0:
                return definitions_data[0]['gloss']
            return ''
        except KeyError:
            return ''


class Verifier:
    def __init__(self, df):
        self.total = len(df.index)
        self.true_positive = 0  # detects ID and matches
        self.false_positive = 0 # detects ID but doesn't match
        # self.true_negative = 0  # doesn't detect ID but didn't mean to
        self.false_negative = 0 # doesn't detect ID

    def match_ids(self, human_id: str, babel_id: str) -> bool:
        if human_id == babel_id:
            self.true_positive += 1
            return True
        elif babel_id == '':
            self.false_negative += 1
        else:
            self.false_positive += 1

        return False

    def calculate_precision(self) -> float:
        precision = self.true_positive / (self.true_positive + self.false_positive)
        return round(precision, 2)

    def calculate_recall(self) -> float:
        recall = self.true_positive / (self.true_positive + self.false_negative)
        return round(recall, 2)

    def calculate_f_score(self) -> float:
        precision = self.calculate_precision()
        recall = self.calculate_recall()
        f_score = 2 * ( (precision * recall) / (precision + recall) )
        return round(f_score, 2)

    def __str__(self):
        precision = self.calculate_precision()
        recall = self.calculate_recall()
        f_score = self.calculate_f_score()
        return f'TOTAL      : {self.total}\n' \
               f'SUCCESS    : {self.true_positive}\n' \
               f'PRECISION  : {precision}\n' \
               f'RECALL     : {recall}\n' \
               f'F-SCORE    : {f_score}'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Perform some text desambiguation through BabelFy API"
    )
    parser.add_argument('--csv', help='Input CSV file to retreive phrases', required=True)
    parser.add_argument('-o', '--out', help='Output File to store CSV result data', required=True)
    args = vars(parser.parse_args())

    df = pd.read_csv(args['csv'], sep=';')
    verifier = Verifier(df)
    babelfynet = BabelFyNet()

    df_result = pd.DataFrame(columns=['phrases', 'word', 'ID', 'definition', 'result_ID', 'result_definition'])
    # df_result = pd.DataFrame()

    print('SUCCESS:')
    for i, row in df.iterrows():
        response_json = babelfynet.disambiguate(
            str(row['phrases']),
            str(row['language'])
        )
        babel_id = babelfynet.get_id_from_babelfy_response(
            response_json,
            #str(row['phrases']),
            int(row['position'])
        )
        matches = verifier.match_ids(
            str(row['ID']),
            babel_id
        )

        definition = babelfynet.download_definition_from_synsetid(str(row['ID']), str(row['language']))
        result_definition = babelfynet.download_definition_from_synsetid(babel_id, str(row['language']))
        temp_df = pd.DataFrame({
            'phrases': row['phrases'],
            'word': row['word'],
            'ID': row['ID'],
            'definition': [definition],
            'result_ID': [babel_id],
            'result_definition': [result_definition],
        })
        # https://www.statology.org/pandas-add-row-to-dataframe/
        # somehow this append a new line to a dataframe
        # df_result.loc[len(df_result.index)] = result_data
        # https://stackoverflow.com/questions/75956209/dataframe-object-has-no-attribute-append
        df_result = pd.concat([df_result, temp_df], ignore_index=True)

        # if matches:
        #     print('\t' + row['phrases'] + ' : ' + row['word'])


    df_result.to_csv(args['out'])

    print()
    print(verifier)
