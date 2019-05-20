from openpyxl import  load_workbook, Workbook
from pathlib import Path
import json

def find_value_range(ws, row, col):
    while ws.cell(row = row, column = col).value != None:
        row += 1
    return row - 1

def do_complex_parsing(ws, row, col, count, parsed_xl_json):
    
    return True

def xl_iterator(ws, ROWS, COLS):
    parsed_xl_json = []
    maxr = init_row = count = 0
    col_index = 1
    row_index = 2

    while col_index <= COLS:    
        while row_index <= ROWS:
            if ws.cell(row = row_index, column = col_index).value != None: # if current cell has value (not None)
                if col_index == 1: # if current column is the serial number
                    count += 1
                    parsed_xl_json.append(dict({
                        count: {}
                        }))
                    print(json.dumps(parsed_xl_json, indent = 4))
                    init_row = maxr = row_index
                    break
                if col_index == 2:
                    maxr = find_value_range(ws, row_index, col_index)
                    questions = ws.iter_cols(min_col = col_index, max_col = col_index, min_row = init_row, max_row = maxr, values_only = True)
                    for question in questions:
                        print('questions: {}'.format(question))
                    row_index = maxr
                if col_index == 3:
                    maxr = find_value_range(ws, row_index, col_index)
                    sources = ws.iter_cols(min_col = col_index, max_col = col_index, min_row = init_row, max_row = maxr, values_only = True)
                    for source in sources:
                        print('source: {}'.format(source))
                    row_index = maxr
                if col_index == 4:
                    maxr = find_value_range(ws, row_index, col_index)
                    relevances = ws.iter_cols(min_col = col_index, max_col = col_index, min_row = init_row, max_row = maxr, values_only = True)
                    for relevance in relevances:
                        print('relevance: {}'.format(relevance))
                    row_index = maxr
                    col_index = 1 # some condition to be added so that infinite loop is avoided
                row_index += 1

            else:
                """ 
                if current cell has no value (is None)
                    1. make row index as first index where data was found
                    2. increment column index
                    3. come out of row iteration
                """
                row_index = init_row
                break
        col_index += 1
        print('Next up: {}r {}c'.format(row_index, col_index))
    return True

if __name__ == "__main__":
    # Load workbook and worksheet
    wb = load_workbook(Path('C:/Users/manikvig/Documents/Work/discovery-file-upload/Assets/mock_data.xlsx'))
    ws = wb['Sheet1']

    # Get total records in the worksheet
    dimensions = ws.calculate_dimension()
    ROWS = int(dimensions.split('A1:D')[1])
    # since format has only 4 columns by default
    COLS = 4
    
    xl_iterator(ws, ROWS, COLS)