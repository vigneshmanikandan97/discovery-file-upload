from openpyxl import  load_workbook, Workbook
from pathlib import Path
import json

# since format has only 4 columns by default
COLS = 4

# Load workbook and worksheet
wb = load_workbook(Path('D:\Vignesh Misc\code\discovery-file-upload\Assets\mock_data.xlsx'))
ws = wb.get_sheet_by_name('Sheet1')

# Get total records in the worksheet
dimensions = ws.calculate_dimension()
ROWS = int(dimensions.split('A1:D')[1])
maxr = init_row = 0

def get_maxr(a, b):
    return a if a > b else b

def xl_iterator(ROWS, COLS):
    row_index = 3
    col_index = 1
    parsed_xl_json = {}

    while row_index <= ROWS:
        while col_index <= COLS:
            if ws.cell(row = row_index, column = col_index).value == None:
                maxr = get_maxr(maxr, row_index)
                col_index += 1
            else:
                if col_index == 1:
                    init_row = row_index
                    parsed_xl_json[ws.cell(row = row_index, column = col_index).value] = {}
                if col_index == 2:
                    maxr = get_maxr(maxr, row_index)
                    questions = ws.iter_cols(min_col = col_index, max_col = col_index, min_row = init_row, max_row = maxr, values_only = True)
                    for question in questions:
                        print('Question: {}'.format(question))
                if col_index == 3:
                    maxr = get_maxr(maxr, row_index)
                    sources = ws.iter_cols(min_col = col_index, max_col = col_index, min_row = init_row, max_row = maxr, values_only = True)
                    for source in sources:
                        print('Sources: {}'.format(source))
                if col_index == 4:
                    maxr = get_maxr(maxr, row_index)
                    relevances = ws.iter_cols(min_col = col_index, max_col = col_index, min_row = init_row, max_row = maxr, values_only = True)
                    for relevance in relevances:
                        print('Relevance: {}'.format(relevance))
                row_index += 1

    return True