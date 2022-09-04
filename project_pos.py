import pandas as pd
import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell

def create() :    
    ## Creating an excel workbook and worksheet
    import datetime
    global workbook
    global worksheet
    workbook = xlsxwriter.Workbook('./output/Billing.xlsx')
    worksheet = workbook.add_worksheet('Bill')
    global row
    global col
    row = 0
    col = 0
    date_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ticket_no = ""
    for i in date_time:
        if (i.isalnum()):
            ticket_no += i
    worksheet.merge_range(row, col, row+3, col+4, "HUNGRY BOX", text_box_center_wrap_format(workbook))
    worksheet.merge_range(row + 4, col, row + 5, col+4, "ADDRESS : E-4/19, Main Market Rd, Ashoka Enclave, Sector 55, Noida, Uttar Pradesh 201309", text_box_center_wrap_format(workbook))
    worksheet.insert_image(row, col, 'logo.png', {'x_scale': 0.6, 'y_scale': 0.6})
    worksheet.merge_range(row + 6, col, row + 6, col+4, "CONTACT : +91 120 353 6938", text_box_center_wrap_format(workbook))
    worksheet.merge_range(row + 7, col, row + 7, col+4, f" Ticket NO. : {ticket_no}" , text_box_center_wrap_format(workbook))
    worksheet.merge_range(row + 8, col, row + 8, col+4, f"DATE-TIME : {date_time}  ", text_box_center_wrap_format(workbook))
    worksheet.merge_range(row + 9, col, row + 9, col+2, "ITEM", text_box_center_wrap_format(workbook))
    worksheet.write(row+9, col+3,"QUANTITY",text_box_center_wrap_format(workbook))
    worksheet.write(row+9, col+4,"PRICE",text_box_center_wrap_format(workbook))
    row = 10
    col = 0
    global sum
    sum = 0
    return date_time, ticket_no

## font name and font size defined

def default_format(workbook):
        
    REGULAR_SIZE = 11
    REGULAR_FONT = 'Cambria'
    default = workbook.add_format({
        'font_name':REGULAR_FONT,
        'font_size':REGULAR_SIZE,
        'valign':'top',
    })
    return default
def text_box_wrap_format(workbook):
    REGULAR_SIZE = 11
    REGULAR_FONT = 'Cambria'
    text_box_wrap = workbook.add_format({
        'font_name':REGULAR_FONT,
        'font_size':REGULAR_SIZE,
        'align':'justify',
        'valign':'vcenter',
        'border':True,
        'text_wrap':True
    })
    return text_box_wrap
def text_box_center_wrap_format(workbook):
    REGULAR_SIZE = 11
    REGULAR_FONT = 'Cambria'
    text_box_center_wrap = workbook.add_format({
        'font_name':REGULAR_FONT,
        'font_size':REGULAR_SIZE,
        'align':'center',
        'valign':'vcenter',
        'border':True,
        'text_wrap':True
    })
    return text_box_center_wrap

def billing(start_call, item_name, quantity, price, finished_call):
    global workbook 
    global worksheet
    if start_call == 1:
        date_time, ticket_no=create()
    global row
    global sum
    # ToDo :: write dataframe into excel file
    worksheet.merge_range(row, col, row, col+2, item_name, text_box_center_wrap_format(workbook)  )
    worksheet.write(row, col+3, quantity, text_box_center_wrap_format(workbook))
    worksheet.write(row,col+4, quantity*price, text_box_center_wrap_format(workbook))
    sum += quantity*price
    # adding next row
    row += 1 
    if finished_call == 1:
        worksheet.write(row, col+3, 'TOTAL', text_box_center_wrap_format(workbook))
        worksheet.write(row, col+4, sum, text_box_center_wrap_format(workbook))
        worksheet.write(row+1, col+3,'TAX', text_box_center_wrap_format(workbook))
        tax = round(sum*0.05)
        worksheet.write(row+1, col+4, tax, text_box_center_wrap_format(workbook))
        worksheet.write(row+2, col+3, 'NET AMOUNT', text_box_center_wrap_format(workbook))
        worksheet.write(row+2, col+4, sum+tax, text_box_center_wrap_format(workbook)) 
        workbook.close()
    if start_call == 1:
        return date_time, ticket_no
