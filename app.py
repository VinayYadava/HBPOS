from flask import Flask, request, jsonify , render_template,redirect,send_from_directory
import flask_excel as excel
import pymongo
from datetime import datetime
import pandas as pd
import project_pos

app = Flask(__name__)
mongo=pymongo.MongoClient("mongodb+srv://vy36689:VY36689@cluster0.xzbxclo.mongodb.net/?retryWrites=true&w=majority")
db=mongo['hungrybox']
db2=mongo['bills_db']
MENU=db['menu']
TEMP=db["temp_bill"]
SALES_COL=db["sales_col"]
DATETIME_OBJECT=datetime.now()
app.config["directory_to_folder"]="./output"
#########################################################################################################
# helper function
def remove(string):
    return string.replace(" ", "")

def Empty(var):
    var=[]
    return var

def temp_bills():
    TEMP.drop()
    table_list,_,_= fetch_temp_bills()
    for i in range(len(table_list)):
        id=table_list[i][0]
        item=table_list[i][1]
        rate=table_list[i][2]
        quant=table_list[i][3]
        TEMP.insert_one({'id':id,"item":item,"rate":rate,"quantity":quant})


def fetch_temp_bills():
    All_entries_bill_dict=[]
    All_entries_bill=[]
    list_keys=[]
    total=0
    tax=0.00
    total_payble=0.00
    t_tp_tax={"tax":tax,"total":total,"total_payble":total_payble}
    x=TEMP.find()
    count=0
    for i in x:
        key_list=[]
        All_entries_bill_dict.append(i)
        e=All_entries_bill_dict[count]
        lisss=list(e.keys())
        list_keys.append(lisss)
        count=count+1
    count=0
    for i in range(len(All_entries_bill_dict)):
        e=All_entries_bill_dict[count]
        if list_keys[i][1]=="tax":
            t_tp_tax={"total":e[list_keys[i][1]],"tax":e[list_keys[i][2]],"total_payble":e[list_keys[i][3]]}
        elif list_keys[i][1]=="id":
            individual_sum=int(e[list_keys[i][3]])*int(e[list_keys[i][4]])
            All_entries_bill.append([e[list_keys[i][1]],e[list_keys[i][2]],e[list_keys[i][3]],e[list_keys[i][4]],individual_sum])
            total=total+e[list_keys[i][3]]*e[list_keys[i][4]]
            tax=round(total/20)
            total_payble=total+tax
            t_tp_tax={"total":total,"tax":tax,"total_payble":total_payble}
        count=count+1
    return All_entries_bill,t_tp_tax
        


def decrease(id):
    doc=TEMP.find_one({'id': id})
    quan=doc['quantity']-1
    if quan==0:
        TEMP.find_one_and_delete({'id': id})
        redirect("/offline_billing")
    TEMP.update_one({'id': id}, {'$set': {'quantity': quan}})
    
    
    
def increase(id):
    doc=TEMP.find_one({'id': id})
    quan=doc['quantity']+1
    TEMP.update_one({'id': id}, {'$set': {'quantity': quan}})
    
    
    
def remove_one(id):
    TEMP.find_one_and_delete({'id': id})

def set_tax_and_total_payble_and_total():
    return 1+2

def prev_tax_and_total_payble_and_total(LIST):
    sum=0
    for i in range(len(LIST)-1):
        sum=sum+LIST[i][2]*LIST[i][3]
    return {"total":sum,"total_payble":round(1.05*sum),"tax":round(0.05*sum)}

###################################################################################################################  
                  
@app.route('/online_billing')
def online_billing():
    TEMP.drop()
    SUPER_TEMP={"total":0,"tax":0,"total_payble":0}
    return render_template("online_billing.html")

@app.route('/')
def index():
    TEMP.drop()
    return render_template("index.html")

@app.route('/support_page')
def support_page():
    TEMP.drop()
    SUPER_TEMP={"total":0,"tax":0,"total_payble":0}
    return render_template("support_page.html")

@app.route('/support_page/Home')
def support_to_home():
    TEMP.drop()
    SUPER_TEMP={"total":0,"tax":0,"total_payble":0}
    return render_template("index.html")
############################################################################################################

#################################################################################
  # this is for updation of menu in MONGODB database by uploading a excel file
#################################################################################
@app.route("/update_food_menu", methods=['GET', 'POST'])
def update_food_menu():
    TEMP.drop()
    SUPER_TEMP={"total":0,"tax":0,"total_payble":0}
    message=""
    if request.method == 'POST':
        MENU.drop()
        Array=request.get_array(field_name='file')
        table_list= [i for i in Array]
        for i in range(len(table_list)):
            if i==0:
                header=[table_list[i][0],table_list[i][1],table_list[i][2],table_list[i][3]]
            else:
                id=table_list[i][0]
                item=table_list[i][1]
                rate=table_list[i][2]
                quantity=table_list[i][3]
                MENU.insert_one({'id':id,"item":item,"rate":rate,"quantity":quantity})
        message= "successfully added"
        return render_template("food_menu.html",message=message)
    return render_template("food_menu.html",message=message)

##########################################################################################################################

##########################################################################################################
# this is for billings in offline mode
##########################################################################################################
@app.route('/offline_billing')
def offline_billing():
    Menu=[]
    total_payble=0
    Tax=0.00
    x=MENU.find()
    TEMP.find_one_and_update
    for i in x:
        Menu.append([i['id'],i['item'],i['rate'],i['quantity']])
    l,tax_total_tpayble =fetch_temp_bills()
    Tax=tax_total_tpayble["tax"]
    total_payble=tax_total_tpayble["total_payble"]
    total=tax_total_tpayble["total"]
    Tax_total_payble_total=[[Tax,total_payble,total]]
    return render_template("offline_billing.html",Menu=Menu , Bill_rows_forms=l,Tax_total_payble_total=Tax_total_payble_total)

###########################################################################################################
@app.route("/add_info_in_bill_table",methods=['GET','POST'])
def add_info_in_bill_table():
    TEMP_LIST,tot_tp_tax=fetch_temp_bills()
    if request.method=='POST':
        id=int(remove(request.form['id']))
        item=request.form['item']
        rate=float(remove(request.form['rate']))
        quantity=int(remove(request.form['quantity']))
        temp_list=[]
        temp_dict={}
        for i in range(len(TEMP_LIST)):
            temp_list.append(TEMP_LIST[i][0])
            temp_dict[f"{TEMP_LIST[i][0]}"]=TEMP_LIST[i][3]
        if id in temp_list:
            Quantity=temp_dict[f"{id}"]+quantity
            TEMP.find_one_and_update({"id":id},{"$set":{"quantity":Quantity}})
            return redirect('/offline_billing')
        TEMP.insert_one({"id":id,"item":item,"rate":rate,"quantity":quantity})
        return redirect('/offline_billing')
    else:
        return redirect('/offline_billing')
#########################################################################################################
@app.route('/decrease_quantity', methods=["GET","POST"])
def decrease_quantity():
    if request.method=='POST':
        id=int(remove(request.form.get('dec_quantity')))
        decrease(id)
        return redirect('/offline_billing')
    return redirect('/offline_billing')
@app.route('/increase_quantity', methods=["GET","POST"])
def increase_quantity():
    if request.method=='POST':
        id=int(remove(request.form.get('inc_quantity')))
        increase(id)
        return redirect('/offline_billing')
    return redirect('/offline_billing')
@app.route('/remove_item', methods=["GET","POST"])
def remove_item():
    if request.method=='POST':
        id=int(remove(request.form.get('remove_item')))
        remove_one(id)
        return redirect('/offline_billing') 
    return redirect('/offline_billing')



##########################################################################
@app.route("/commit_bill")
def commit_bill():
    filename="Billing.xlsx"
    bill_list=[]
    q,_=fetch_temp_bills()
    for i in q:
        a=i[0]
        b=i[1]
        c=i[2]
        d=i[3]
        dictt={"id":a,"item":b,"rate":c,"quantity":d }
        bill_list.append(dictt)
    start = 1
    end = 0
    for i in range(len(bill_list)):
        if start == 1 :
            date_time, ticket_no =project_pos.billing(start, bill_list[i]['item'], bill_list[i]['quantity'], bill_list[i]['rate'], end)
        else:
            project_pos.billing(start, bill_list[i]['item'], bill_list[i]['quantity'], bill_list[i]['rate'], end)

        start = 0
        if i >= len(bill_list) - 2:
            end = 1
        Ticket_coll=db2[f"{ticket_no}"]
        sum=0
        for i in q:
            a=i[0]
            b=i[1]
            c=i[2]
            d=i[3]
            dictt={"id":a,"item":b,"rate":c,"quantity":d }
            sum=sum+(c*d)
            Ticket_coll.insert_one(dictt)
    SALES_COL.insert_one({"ticket_no":ticket_no ,"ammount":sum})
    return redirect("/print")

@app.route("/print")
def print():
    return render_template("print.html")

@app.route("/print_bill")
def print_bill():
    TEMP.drop()
    filename="Billing.xlsx"
    return send_from_directory(app.config["directory_to_folder"], filename, as_attachment=True)

@app.route("/updated_menu")
def updated_menu():
    Menu=[]
    x=MENU.find()
    TEMP.find_one_and_update
    for i in x:
        Menu.append([i['id'],i['item'],i['rate'],i['quantity']])
    return render_template("updated_menu.html",Menu=Menu)



# insert database related code here
if __name__ == "__main__":
    excel.init_excel(app)
    app.run(host="127.0.0.1",port=3000,debug=True)