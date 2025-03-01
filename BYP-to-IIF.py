my_mode="WC"
my_date="01/05/2029"
my_customer="LSI"
# BYP to IIF
#
# 0.1
# 0.2
# We want to create a .iif file in a directory
# Let's start with the basics of an LSI .csv file
# And thinking through the different inputs
# WC files contain multiple transactions
# LSI files
# Should generate a purchase .iif and a sale .iif. Unless they can be combined?
# Title {Would be generated via ISBN lookup}
# MTD_pub_comp  {eliding print and distribution charges}
# MTD_Quantity

import ldy_utils
from ldy_utils import install_and_import
import sys
install_and_import('sqlite3')
import sqlite3
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP

from colorama import init, Fore, Style

# Initialize colorama (this is especially important for Windows)
init(autoreset=True)

import subprocess

import sys
import importlib
from gettext import install

from ldy_utils import quick_exit

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkcalendar import DateEntry


# install_and_import move to LDY utils
# ### Some utility functions

# Example usage
install_and_import('openpyxl')
install_and_import('pandas', 'pd')  # Now you can use 'pd' as an alias for pandas
import pandas as pd
df = pd.DataFrame() # just so we have it to kick around
pd.set_option('display.width', 240)

install_and_import('sqlite3','sqlite3')
import random
random.seed()
import atexit
# Set a global variable for the output stream
output = sys.stdout

def set_output(filename=None):
    global output
    if filename:
        output = open(filename, 'w') # overwrite
    else:
        output = sys.stdout

def print_output(message):
    print(message, file=output)

def close_output():
    global output
    if output != sys.stdout:
        output.close()

atexit.register(close_output)

# We're going to start by importing ISBN-13 / Item colums from QuickBook TitleList in the database and build a dictionary

# Establish a global connection to the database
db_path = "c:\\Data\\Python\\book_data.db"
conn = sqlite3.connect(db_path)
conn.close()
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Execute the query to select all titles from BYP_Titles
    # okay, let's change this to also create a wcproductid_to_item dictionary
    cursor.execute('SELECT  CAST("ISBN-13" AS TEXT) AS "ISBN-13", Item,CAST(ProductNumber AS TEXT) as ProductNumber FROM "QuickBook TitleList" WHERE "ISBN-13" <>"" OR "ItemProductNumber" <> ""  ')

    # Fetch all results
    rows = cursor.fetchall()

    # Create a defaultdict to hold ISBN-13 as keys and Items as values
    isbn_to_item = defaultdict(str)
    wc_id_to_item= defaultdict(str)
    # print ("Wherefore art our row? Here thou art!",rows
    # Populate the dictionary
    for row in rows:
        isbn, item, product_id = row
        if (isbn):
            isbn_to_item[isbn] = item.strip()
        if (product_id):
            wc_id_to_item[product_id]=item.strip()
        # print ("POPULATING the dictionary while looping over rows ")
        print(f'Current entry: product_id {product_id} -> {wc_id_to_item[product_id]}')

        # print (f'wc_id_to_item {wc_id_to_item} maps to product_id {product_id}')

    # Example of accessing the dictionary
    #for isbn, item in isbn_to_item.items():
    #    print(f"ISBN-13: {isbn}, Item: {item}")


except sqlite3.Error as e:
    print(f"An error occurred: {e}")

finally:
    # Close the connection after the debugging is done
    conn.close()


# Now to define some functions

def get_title_by_isbn(isbn):
    try:
        # Query to get the title based on ISBN
        cursor.execute("SELECT Title FROM BYP_Titles WHERE ISBN = ?", (isbn,))
        result = cursor.fetchone()

        # Check if a result was found and return the title or a message if not found
        if result:
            return result[0]
        else:
            return "ISBN not found in database."

    except sqlite3.Error as e:
        return f"An error occurred: {e}"

# Testing the function

isbn_list = ["9781953829818", "9780987654321"]  # Replace with the list of ISBNs you're searching for
'''
for isbn in isbn_list:
    title = get_title_by_isbn(isbn)
    # print(f"The title for ISBN {isbn} is: {title}")
'''

# Close the connection when done
conn.close()

#  print (return_qbitem_from_isbn(9781953829818))

# Set output to a file
# And now we are hard coding the files....
# as we get each input stream to work
# So this section customizes the terminology for each input source


import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkcalendar import DateEntry


my_csv='byp_iif\\24sales_comp.xlsx'
my_KDP_xls="byp_iif\\KDP_Orders.xlsx"

def main_program(mode, file_path, date_value):
    my_mode=mode
    my_date=date_value

    data = defaultdict(dict)
    exchangeMultiplier={
        'USD': 1,
        'CAD': 0.73,
        'GBP': 1.28,
        'INR': 0.01195,
        'AUD': 0.66,
        'EUR': 1.0822,
        'JPY': 0.006610,
        'MXN': 0.05488,
        'BRL': 0.1863,
        'SEK': 0.09464
    }


    df=pd.DataFrame()  # just so we have it to kick around
    pd.set_option('display.width', 240)
    '''data["LSI"]["inputfile"]=my_csv
    data["KDP"]["inputfile"]=my_KDP_xls
    data["PD"]["inputfile"]='byp_iif\\PD_Sales_report.xlsx'
    data["WC"]["inputfile"]='byp_iif\\byp-test-single.csv' '''

    data["LSI"]["inputfile"]=file_path
    data["KDP"]["inputfile"]=file_path
    data["PD"]["inputfile"]=file_path
    data["WC"]["inputfile"]=file_path

    data["WC"]["title"]="Product Name"
    data["WC"]["isbn"]="Product Id"
    data["WC"]["quantity"]="Quantity"
    data["WC"]["amount"]="Item Cost"
    data["WC"]["customer"]="Web customer"
    data["WC"]["account"]="Web customer"
    data["WC"]["lookuptable"]= wc_id_to_item


    data["LSI"]["title"]="title"
    data["LSI"]["quantity"]="PTD_Quantity"
    data["LSI"]["amount"]="PTD_pub_comp"
    data["LSI"]["customer"]="Lightning Source Wholesale"
    data["LSI"]["isbn"]="isbn_13"
    data["LSI"]["account"]="LSI"
    data["LSI"]["lookuptable"]=isbn_to_item

    data["KDP"]["title"]="Title"
    data["KDP"]["isbn"]="ASIN/ISBN"
    data["KDP"]["quantity"]="Net Units Sold"
    data["KDP"]["amount"]="Royalty"
    data["KDP"]["customer"]="Kindle"
    data["KDP"]["account"]="Amazon Kindle"
    data["KDP"]["lookuptable"]=isbn_to_item

    data["PD"]["title"]="Title"
    data["PD"]["isbn"]="Isbn"
    data["PD"]["quantity"]="Quantity"
    data["PD"]["amount"]="Royalty all usd"
    data["PD"]["customer"]="PublishDrive"
    data["PD"]["account"]="Publish Drive"
    data["PD"]["lookuptable"]=isbn_to_item

    out_dir: str='byp_iif\\'
    out_file=my_mode
    set_output(out_dir+out_file+'.iif') # Or set to stdout # set_output()


    isbnFieldName=data[my_mode]["isbn"]
    titleFieldName=data[my_mode]["title"]

    # Load the CSV file into a DataFrame
    match my_mode:
        case "WC":
            '''
            So, we have to do some preprocessing before we load it into the frame -- or after. 
            We need to loop through chucks of an order
            Break out tax and fees into separate orders of the form item/price/xxxx
            Look up item_product_id and replace it with isbn
            Or, we load into one frame before passing into another
            
            Key columns:
            data["WC"]["item_name"]="item_name"
            data["WC"]["isbn"]="item_product_id"
            data["WC"]["quantity"]="item_quantity"
            data["WC"]["amount"]="item_subtotal"
            data["WC"]["customer"]="Web customer"
            data["WC"]["account"]="Web customer
            
            S&H
            WooCommerce fee
            
            
            '''
            # Load in data["WC"]["inputfile"] to temporary dataframe
            # data["WC"]["inputfile"]='byp_iif\\byp-test-single.csv'
            # 		First Name 	Last Name 	State Code (Shipping)	Country Code (Shipping)
            # 				Product Id	Variation Id	Product Variation	Quantity	Item Cost	Order Line Total (- Refund)	Order Line (w&#x2F;o tax)	creditcard_fee	Order Total Fee	Stripe Fee	Order Line Tax	Discount Amount	Cart Tax Amount	Order Shipping Amount

            columns_to_import=['Order ID', 'Order Date','Order Total Amount','Product Id','Variation Id','Product Name','Item Cost','Quantity']
            all_columns_df=pd.read_csv(data[my_mode]["inputfile"], dtype=str)
            print (f'SOME COLUMNS OF THE DATAFRAME< FRESHULY IMPORTED from {data[my_mode]["inputfile"]}!')
            selected_columns=['Product Id','Product Name','Variation Id'] #'order_total',
            print(all_columns_df[selected_columns])


            # Filter to include only the columns that exist in the CSV
            available_columns=[col for col in columns_to_import if col in all_columns_df.columns]

            # Select only available columns
            import_df=all_columns_df[available_columns]

            # import_df=pd.read_csv(data[my_mode]["inputfile"], dtype=str,usecols=columns_to_import)
            # Loop over inputfile
                # chunk the first order
                # process order rows to make fees, taxes, and bundles appropriate
                # The new items contain item_name

                # put process rows into processed dataframe, df
            for order_id, temp_df in import_df.groupby('Order ID'):
                # Process the temp_df for the current order
                # For demonstration, let's add a column indicating processed
                temp_df=temp_df.copy()  # Avoid modifying the original DataFrame
                temp_df['processed']=True  # Example processing
                # Is there shipping?
                # Check if the "shipping_total" column exists
                if 'shipping_total' in temp_df.columns:  # product # is -1,  as maintained manually in the db
                    # Check if all values are the same
                    unique_values=temp_df['shipping_total'].unique()

                    if len(unique_values) == 1:
                        print(f"The column 'shipping_total' has a single unique value: {unique_values[0]}")
                        if not pd.isna(unique_values[0]): # make sure it's not nothing

                            # Append a row with
                            # create a row where item_name="S&H",item_subtotal=unique_values[0],item_quantity=1, //price or quantity?
                            my_row=pd.DataFrame({"item_name": ["S&H"], "item_subtotal": [unique_values[0]], "item_quantity": [1],"item_product_id":[-1]})
                            df=pd.concat([df, my_row], ignore_index=True)
                            print("adding...\n ",my_row,"\n....to df dataframe")
                            ## But.... we're not adding to the proper total. Why is that????

                    elif len(unique_values) > 1:
                        print(f"The column 'shipping_total' has multiple unique values: {unique_values}")
                        # We should fail cause this is weird
                    else:
                        print("The column 'shipping_total' exists but is empty (all values are NaN).")
                else:
                    print("The column 'shipping_total' does not exist in the DataFrame.")

                # Append the processed temp_df to the final DataFrame
                df=pd.concat([df, temp_df], ignore_index=True)
        case "LSI":
            # df = pd.read_csv(my_csv,dtype={"isbn_13": str})
            # df = pd.read_excel(data["LSI"]["inputfile"], dtype={"isbn_13": str,"isbn": str})
            df=pd.read_csv(
                data["LSI"]["inputfile"],
                sep='\t',
                encoding='latin1',  # or try 'cp1252' if needed
                dtype={"isbn_13": str, "isbn": str}
            )
            backup_LSI_df=df # let's make a backup ,

            # Now we need to multiply the values by the exchange rate
            selected_currency=my_currency_var.get()  # Get the selected currency as a string

            if selected_currency not in exchangeMultiplier:
                raise ValueError(f"Unknown currency selected: {selected_currency}. Aborting.")

            exchange_rate=exchangeMultiplier[selected_currency]  # Fetch the exchange rate
            df["PTD_pub_comp"]=df["PTD_pub_comp"] * exchange_rate  # Apply the conversion

            df['isbn_13'] = df['isbn_13'].astype(str)
            pd.set_option('display.float_format', '{:.0f}'.format)  # Affects display only, not data type
            print(df['isbn_13'].dtype)
            df['isbn_13'] = df['isbn_13'].apply(str)
            print(df[['isbn_13', 'title']])

        case "KDP":
            df = pd.read_excel(data["KDP"]["inputfile"], sheet_name='Combined Sales',dtype={data["KDP"]["isbn"]: str})
            df["Royalty"]=df["Royalty"] * df["Currency"].map(exchangeMultiplier)
            missing_currencies=df[~df["Currency"].isin(exchangeMultiplier.keys())]["Currency"].unique()
            if missing_currencies.size > 0:
                raise ValueError(f"Unknown currency detected: {missing_currencies}. Aborting.")

            # Loop through and adjust for currency
            # If column "Currency" != USD
            # royalty = royalty * ExchangeMultiplier[currency]


        case "PD":
            print(data["PD"]["inputfile"])
            df = pd.read_excel(data["PD"]["inputfile"], sheet_name='Raw data',dtype={data["PD"]["isbn"]: str})

    ''' And now, we process what is in the df dataframe
    '''

    '''
    # If it's a LSI/KDP/PD report, then we look up by isbn. But if it's a WC, we look up by product #. 
    So we can either fork on this. Or we can look up the isbn when we process the WC input. 
    But what we want to end up with is the item name from the lookup table. Which is the same lookup as the isbn, only different. So let's case this joint
    
    So in addition to creating isbn_to_item, we should create wcproductid_to_item
    
    '''


    df[isbnFieldName] = df[isbnFieldName].str.strip()
    #print (df[isbnFieldName])
    #print(df[isbnFieldName][1])
    #ldy_utils.quick_exit()
    # Filter the rows where the ISBN is not in isbn_to_item

    # if (my_mode != 'WC'): #first the original way
    print (f''' Let's unpack this:)
            found_isbns=df[df[isbnFieldName].isin(data[my_mode]["lookuptable"].keys())]
            where df[df[{isbnFieldName} is checked if in {data[my_mode]["lookuptable"]}
            ''')

    print ("As per CHATGPT REQUEST!")
    print ("First the type:")
    print(type(data[my_mode]["lookuptable"]))
    print ("Now the data:")
    print(data[my_mode]["lookuptable"])
    #print("Now the Keys:")
    #print(keys)

    print ("isbnFieldName")
    print (df[isbnFieldName])
    keys = list(data[my_mode]["lookuptable"].keys())


    filtered_df = df[df[isbnFieldName].notna()]
    print("Filtered_DF:")
    print(filtered_df)

    # Get the column name from the data structure
    column_name = data[my_mode]["isbn"]

    # Check if the column exists in the DataFrame
    if column_name in df.columns:
        print(f"The column '{column_name}' exists in the DataFrame.")
    else:
        print(f"The column '{column_name}' does NOT exist in the DataFrame.")
        print(f"Available columns in the DataFrame are: {list(df.columns)}")

    keys = [str(key) for key in keys]
    filtered_df = filtered_df.copy()
    filtered_df.loc[:, isbnFieldName] = filtered_df[isbnFieldName].astype(str)


    # Now perform the .isin() check
    found_isbns = filtered_df[filtered_df[isbnFieldName].isin(keys)]
    assert isbnFieldName in filtered_df.columns, f"'{isbnFieldName}' is not a valid column in the DataFrame."
    # assert '138' in keys, f"138is not in keys"
    keys.sort()
    print(keys)
    # assert '39511' in keys, f"39511 is not in keys"

    found_data = found_isbns[[isbnFieldName, titleFieldName,'Variation Id']]

    print("Printing found_data")
    print (found_data)
    found_data  = found_data.drop_duplicates(subset=[isbnFieldName]).sort_values(by=titleFieldName)

    missing_isbns = filtered_df[~filtered_df[isbnFieldName].isin(keys)]

    # Create a new DataFrame with only the missing ISBNs and their corresponding titles
    missing_data = missing_isbns[[isbnFieldName, titleFieldName]]
    # if  my_mode == "WC":
    #    missing_data = missing_isbns[isbnFieldName, titleFieldName, 'Variation Id']

    # Remove duplicate ISBNs, keeping only the first occurrence of each ISBN
    missing_data  = missing_data.drop_duplicates(subset=[isbnFieldName]).sort_values(by=titleFieldName)

    # Display the deduplicated DataFrame for verification
    print(f"{Fore.GREEN}\nHere is your Missing ISBNs, Oh Ben Yehuda!\n")
    print(f"{Fore.GREEN}\n{missing_data}")

    print("\nHere is your Found ISBNs, Oh Ben Yehuda!\n")
    print(found_data)
    # print(isbn_to_item.keys())
    print(len(missing_data), " ISBNs are missing")
    print(len(found_data), " ISBNs were found")
    # sys.exit("those are the holes in your data, friends!")


    # Display the first few rows
    print(df.head())






    print("Hello world, this is BYP to IIF ")
    from collections import OrderedDict

    ## And now, we prep to export to a quick book transaction file

    class TRNS:
        def __init__(self, header_names, header_values):
            # Split the input strings into lists for field names and corresponding values
            self.field_names = header_names.split(',')
            values = header_values.split(',')

            # Convert all values to strings to ensure consistent handling
            values=[str(value) for value in values]

            # Initialize fields as an OrderedDict pairing field names with values
            self.fields=OrderedDict(zip(self.field_names, values))

        def update_field(self, field_name, value):

            if isinstance(value, Decimal):
                # If Decimal, quantize to two decimal places for consistency
                value=value.quantize(Decimal('0.01'))
            elif isinstance(value, (int, float)):
                # Convert numbers to Decimal and quantize
                value=Decimal(value).quantize(Decimal('0.01'))
            else:
                # Otherwise, ensure it's stored as a string
                value=str(value)

            if field_name in self.fields:
                self.fields[field_name] = value


        def export_to_csv(self):
            # Convert the OrderedDict to a CSV row, keeping blanks intact
            return ','.join([str(self.fields[key]) if self.fields[key] is not None else '' for key in self.fields])

    ## Too much of this may still be hardcoded -- will need to check

    theader_names ="TRNS,TRNSID,TRNSTYPE,DATE,ACCNT,NAME,CLASS,AMOUNT,DOCNUM,MEMO,CLEAR,TOPRINT,NAMEISTAXABLE,ADDR1,ADDR2,ADDR3,ADDR4,ADDR5,DUEDATE,TERMS,PAID,PAYMETH,SHIPVIA,SHIPDATE,OTHER1,REP,FOB,PONUM,INVTITLE,INVMEMO,SADDR1,SADDR2,SADDR3,SADDR4,SADDR5,PAYITEM,YEARTODATE,WAGEBASE,EXTRA,TOSEND,ISAJE,,,,,,,,,,,,,,,,,,"
    theader_values = "TRNS,110,CASH SALE,7/1/2026,Undeposited Funds,Larry Yudelson (not a vendor),,210,100,Memo Goes Here,N,N,Y,,,,,,7/27/2096,,N,,,7/27/2026,,,,,,,,,,,,,,,,N,N,,,,,,,,,,,,,,,,,,"
    sheader_names="SPL,TRNSTYPE,SPLID,DATE,ACCNT,NAME,CLASS,AMOUNT,DOCNUM,MEMO,CLEAR,QNTY,PRICE,INVITEM,PAYMETH,TAXABLE,VALADJ,REIMBEXP,SERVICEDATE,OTHER2,OTHER3,PAYITEM,YEARTODATE,WAGEBASE,EXTRA,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,"
    s_default_values="SPL,111,CASH SALE,7/29/2026,Income Account,,Class Name,-100,,,N,-10,10,Another Book,,N,N,NOTHING,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,"
    s_tax_line="SPL,113,CASH SALE,7/29/2026,Sales Tax Payable,Vendor,,-10,100,Sales Tax,N,,10.00%,Sales Tax,,N,N,NOTHING,,,,,,,AUTOSTAX,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,"
    end_trans_header="ENDTRNS,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,"
    end_trans_values="ENDTRNS,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,"

    def print_iff_headers():
        print_output("!" + theader_names)
        print_output("!" + sheader_names)
        print_output("!" + end_trans_header)

    def print_iff_eof():
        print_output(end_trans_values)

    print_iff_headers()
    my_TRNS = TRNS(theader_names, theader_values)
    my_TRNS.update_field("DATE",my_date)
    my_TRNS.update_field("NAME",data[my_mode]["customer"])
    my_TRNS.update_field("ACCNT",data[my_mode]["account"])
    my_TRNS.update_field("MEMO",file_path + " Imported by BYP-to-IIF.py")



    sale_lines=[]
    total_amount=calculated_total_amount=decimaled_total_amount=0


    ## Looks like this is still being tested.....

    my_Sale: TRNS=TRNS(sheader_names, s_default_values)
    my_Sale.update_field("INVITEM", "Name")
    my_Sale.update_field("QNTY", 3 * -1)
    my_Sale.update_field("AMOUNT",100*-1)
    my_price=33.33
    my_Sale.update_field("PRICE",my_price)

    print(f"@*| {my_Sale.export_to_csv()}|")

    for index, row in filtered_df.iterrows():

        title=row[data[my_mode]["title"]]
        mtd_quantity=row[data[my_mode]["quantity"]]
        # mtd_pub_comp=Decimal(row[data[my_mode]["amount"]])
        mtd_pub_comp=row[data[my_mode]["amount"]]
        #print ("isbn column ",data[my_mode]["isbn"])
        isbn=data[my_mode]["isbn"]
        #print ("this isbn: ",row[data[my_mode]["isbn"]])
        # print (data[my_mode]["lookuptable"])
        # print ('This isbn is ',row[data[my_mode]["isbn"]])

        # item=data[my_mode]["lookuptable"][row[data[my_mode]["isbn"]]]
        key=str(row[data[my_mode]["isbn"]])  # Convert to str
        item=(data[my_mode]["lookuptable"])[key]
        print('data[my_mode]["lookuptable"]',data[my_mode]["lookuptable"])
        title = item.split(':')[0]
        title=title[:25]


        if mtd_quantity:
            print(f"Item: {item}, ISBN: {row[data[my_mode]['isbn']]} PTD_Quantity: {mtd_quantity}")
            if (item==""):
                print("Item is blank for ISBN ", row[data[my_mode]['isbn']])
            my_Sale: TRNS=TRNS(sheader_names, s_default_values)
            my_Sale.update_field("INVITEM",  item)
            decimalQuantity=Decimal(mtd_quantity) * Decimal('-1').quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            my_Sale.update_field("QNTY", str(decimalQuantity))
            decimalAmount= (Decimal(mtd_pub_comp) * Decimal('-1')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            my_Sale.update_field("AMOUNT",str(decimalAmount))

            # print("@@@",mtd_pub_comp, mtd_quantity)
            decimalPrice=Decimal(Decimal(mtd_pub_comp) / Decimal(mtd_quantity)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            my_price=str(decimalPrice)
            my_Sale.update_field("PRICE",str(decimalPrice))
            # print(f"*| {my_Sale.export_to_csv()}|")
            sale_lines.append(my_Sale)
            total_amount+=Decimal(mtd_pub_comp)
            calculated_total_amount +=Decimal(decimalPrice*decimalQuantity)
            decimaled_total_amount +=decimalAmount




    # Adjust for rounding errors
    my_Adjustment: TRNS=TRNS(sheader_names, s_default_values)
    my_Adjustment.update_field("INVITEM", 'Misc Sales Revenuue')
    my_Adjustment.update_field("QNTY", -1)
    my_Adjustment_amount=(decimaled_total_amount-calculated_total_amount)*-1
    my_Adjustment.update_field("AMOUNT", str(my_Adjustment_amount*-1))
    my_Adjustment.update_field("PRICE", str(my_Adjustment_amount))
    # sale_lines.append(my_Adjustment)

    my_taxrate=0
    my_taxamount=my_taxrate*total_amount
    my_Tax = TRNS(sheader_names,s_tax_line)
    my_Tax.update_field("AMOUNT",my_taxamount*-1)
    my_Tax.update_field("PRICE","0%")
    my_Sale= TRNS(sheader_names,s_default_values)

    #my_Trans_amount=total_amount+my_taxamount
    my_Trans_amount=decimaled_total_amount*-1

    my_TRNS.update_field("AMOUNT",str(my_Trans_amount))

    print_output(my_TRNS.export_to_csv())

    # After looping through the DataFrame, iterate over TRNS objects

    rows_to_output = len(sale_lines)  # Set it to the length of the list
    i=0
    #rows_to_output=2
    for sale in sale_lines[:rows_to_output]:
        # Export TRNS objects to CSV format (or process them as needed)
        csv_output = sale.export_to_csv()
        # print_output(csv_output)
        i+=1
        print_output(csv_output)
        print(f"|{i}: {csv_output}|")
    print_output(my_Tax.export_to_csv())
    print_output(end_trans_values)
    print_iff_eof()
    close_output()
    print('total_amount=',total_amount, 'calculated_total_amount=', calculated_total_amount,'decimaled_total_amount=',decimaled_total_amount)
    #, So, what does QB need to receive when importing a transaction?
    #  A transaction contains

    # Transaction number !!
    # TRNS|SPL
    # We have two scheme here, one for TRNS and one for SPL
    # I want to ingest the csv row to create the data
    # Each sales line in incomving report becomes a SPL
    # The SPL calculates the TRNS
    # So, export the header, then TNS, and then SPL
    # And then ENDTRNS
    # Transaction number
    # Account: Income Account|Undeposited Funds|Sales Tax Payable


def browse_file():
    """
    Open a file dialog to select a file from the folder "byp_iif\\".
    """
    # Adjust the initial directory as needed.
    file_path=filedialog.askopenfilename(
        initialdir="byp_iif\\",
        title="Select file",
        filetypes=(("All Files", "*.*"),)
    )
    if file_path:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, file_path)


def submit():
    """
    Gather the selected values and proceed with your program logic.
    """
    mode=mode_var.get()
    file_path=file_entry.get()
    # DateEntry widget returns a date string; you can also get a datetime.date using get_date()
    date_value=date_entry.get_date()

    # For demonstration, we simply print the selected values.
    print("Selected Mode: ", mode)
    print("Selected File: ", file_path)
    print("Selected Date: ", date_value)


    # Inform the user that the selections have been received.
    messagebox.showinfo("Selection Received",
                        f"Mode: {mode}\nFile: {file_path}\nDate: {date_value}")
    # Example: You might call your main function here with the selected options.
    main_program(mode, file_path, date_value)


# Create the main application window
root=tk.Tk()
root.title("My Program GUI")

# Create a frame to contain the widgets with some padding
frame=tk.Frame(root, padx=10, pady=10)
frame.pack()

# --- Mode Selection ---
tk.Label(frame, text="Select Mode:").grid(row=0, column=0, sticky="w", pady=5)
mode_var=tk.StringVar(value="WC")  # Default value
modes=["WC", "KDP", "PD", "LSI", "PB"]
mode_menu=ttk.OptionMenu(frame, mode_var, modes[0], *modes)
mode_menu.grid(row=0, column=1, sticky="w", pady=5)

# --- File Selection ---
tk.Label(frame, text="Select File:").grid(row=1, column=0, sticky="w", pady=5)
file_entry=tk.Entry(frame, width=50)
file_entry.grid(row=1, column=1, sticky="w", pady=5)
browse_button=tk.Button(frame, text="Browse...", command=browse_file)
browse_button.grid(row=1, column=2, padx=5, pady=5)

# --- Date Selection ---
tk.Label(frame, text="Select Date:").grid(row=2, column=0, sticky="w", pady=5)
# DateEntry provides a calendar popup and also allows text input.
date_entry=DateEntry(frame, width=12, background='darkblue', foreground='white', borderwidth=2,
                     date_pattern='yyyy-mm-dd')
date_entry.grid(row=2, column=1, sticky="w", pady=5)

# --- My Currency Selection ---
tk.Label(frame, text="Select Currency:").grid(row=3, column=0, sticky="w", pady=5)
my_currency_var = tk.StringVar(value="USD")  # Default currency
currencies = ["USD", "AUD", "GBP"]
currency_menu = ttk.OptionMenu(frame, my_currency_var, currencies[0], *currencies)
currency_menu.grid(row=3, column=1, sticky="w", pady=5)

# --- Submit Button ---
submit_button=tk.Button(frame, text="Submit", command=submit)
submit_button.grid(row=3, column=0, columnspan=3, pady=10)

# Start the GUI event loop
root.mainloop()


