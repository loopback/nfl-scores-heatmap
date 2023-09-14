#!/usr/bin/env python

import time
import math
import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup


def main():
    first_year = 1922
    last_year = 2022

    data = []

    # --------------------------------------------------------------------------
    #   download data
    # --------------------------------------------------------------------------
    for year in range(first_year, last_year + 1):
        print(str(year) + '...')
        url = f'https://www.pro-football-reference.com/years/{year}/games.htm#games'
        response = requests.get(url)

        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find("table", {'id': 'games'})

        # clean out metadata rows
        for row in table.find_all('tr'):
            if (
                row.get("class") == ['thead']
                or row.get("class") == ['stathead']
                or row.get("class") == ['rowSum']
            ):
                row.decompose()

        df = pd.read_html(str(table))[0]
        for _, row in df.iterrows():
            # 'Pts' is the winning score, 'Pts.1' is the losing score
            temp = [row['Pts'], row['Pts.1']]
            if all(
                isinstance(x, (int, float))
                and not math.isnan(x)
                for x in temp
            ):
                temp = [int(x) for x in temp]
                data.append(temp)

        # delay to avoid exceeding rate limit
        if year != last_year:
            time.sleep(3)

    # --------------------------------------------------------------------------
    #   generate matrix
    # --------------------------------------------------------------------------

    # create matrix where each column is the winning score, each row is the
    # losing score, and each cell is the number of times that score combination
    # occurred
    a = max(max(data))
    matrix = np.zeros((a + 1, a + 1))
    matrix = matrix.astype(int)

    for row in data:
        matrix[row[0]][row[1]] += 1
    matrix = matrix.transpose()         # switch from lower to upper triangular

    # set impossible entries (either team scores 1 point) and lower diagonal
    # entries to -1
    for i in range(0, len(matrix)):
        for j in range(0, len(matrix)):
            if i > j or i == 1 or j == 1:
                matrix[i][j] = -1

    # --------------------------------------------------------------------------
    #   save matrix to csv file
    # --------------------------------------------------------------------------

    # save matrix to csv with no header row or index column
    df = pd.DataFrame(matrix)
    df.to_csv('nfl_matrix.csv', index=False, header=False)


if __name__ == '__main__':
    main()
