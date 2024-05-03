from ast import Mod
from flask import Blueprint,render_template,request,send_file,session,redirect,flash
from numpy import concatenate
from fpdf import FPDF,HTMLMixin
import pyodbc
from datetime import datetime,time
from models.add_count import add_count
from models.read_inquiry import read_inquiry
import time
import base64
from models.mail_RFQ import mail_RFQ
import os.path 
import pandas as pd

# import os

RFQ=Blueprint("RFQ",__name__,template_folder='templates',static_folder='static')


class PDF(FPDF,HTMLMixin):

  
  def __init__(self,inquiry_number,No_of_items,petra_codes,desc,qty,unit,suppliers1):
    super(PDF,self).__init__()
    self.inquiry_number=inquiry_number
    self.No_of_items=No_of_items
    self.petra_codes=petra_codes
    self.desc=desc
    self.qty=qty
    self.unit=unit
    self.suppliers1=suppliers1
    self.current_date = datetime.today().date()
  def header(self):
    
    # PETRA logo
    self.image("Z:/M.HAMMAD/PY/My_Apps/static/imgs/PETRA_LOGO.png",x=80,y=5,w=50)
    self.set_font('Arial', 'B', 8)
    
    
    ## PROJECT NAME
    
    self.multi_cell(w=25,h= 4,txt= f"RFQ#:{self.inquiry_number}\nDate:{self.current_date}",border=1, align='L')
    self.set_xy(192, 8)
    self.cell(15,6,f' Page{self.page_no()}/{{nb}}',align="C",border=1,ln=1)
    self.ln(11)
    
    
    
    
    
    
    
  # def footer(self):
  #   self.set_y(-8)
  #   self.set_font('Arial', 'I', 10)
  #   self.cell(0,10,f'Page{self.page_no()}/{{nb}}',align="C")




 

@RFQ.route("/RFQ",methods=["GET","POST"])#post means to post to server, get means to get from server.


def RFQ_func():
  # print("hereee")
  
  if "user"in session:
    username=session["user"]
  
  if request.method=="POST":

    
    No_of_items=[]
    petra_codes=[]
    desc=[]
    desc_list=[]
    qty=[]
    unit=[]
    supplier=[]
    emails=[]
    emails1=[]
    final_emails=[]
    conn = pyodbc.connect('Driver={SQL Server Native Client 11.0};'
                      'Server=PEEDM-HAMAD;'
                      'Database=usersDB;'
                      'Trusted_Connection=yes;')
    cursor=conn.cursor()
    
    query=f"SELECT Supplier FROM suppliers"
    rows=cursor.execute(query)
    rows=rows.fetchall()
    # conn.commit()
    # conn.close()
    if rows:
      
      for row in range (0,len(rows)):
        
        supplier.append(rows[row]) 
      supplier = [item for t in supplier for item in t]  #convert list of tubles coming from SQL to list


    inquiry= request.files['inquiry']
    # inquiry=os.path.abspath(inquiry)
    # print(inquiry)
    inquiry.save(f"Z:/M.hammad/saved_inquiries/{(inquiry.filename)}")
    # inquiry.save('Z:/M.hammad/saved_inquiries/'(inquiry.filename))
    # inquiry=inquiry.filename
    full_file_path=f"Z:/M.hammad/saved_inquiries/{(inquiry.filename)}"
    print(full_file_path)
    # supplier=request.form['supplier'] ##### this data come from excel sheet

    if not inquiry:
      flash('No file selected', "error")
    
    else:
      if  inquiry.filename.endswith('xlsx') or inquiry.filename.endswith('xls'):
        print("yes, it ends with xlxs or xls")
        inquiry_number=read_inquiry(full_file_path).inquiry_number
        No_of_items=read_inquiry(full_file_path).No_of_items
        petra_codes=read_inquiry(full_file_path).petra_codes
        desc=read_inquiry(full_file_path).desc
        qty=read_inquiry(full_file_path).qty
        unit=read_inquiry(full_file_path).unit
        suppliers1=request.form['suppliers1'] 
       
        print(inquiry_number)
        
        


        # get supplier email if exist
        query=f"SELECT email1,email2,email3,email4,email5,email6,email7,email8 FROM suppliers WHERE Supplier='{suppliers1}'"
        rows=cursor.execute(query)
        rows=rows.fetchall()
        conn.commit()
        conn.close()
        if rows:
          for row in range (0,len(rows)):
            
            emails.append(rows[row]) 
          emails = [item for t in emails for item in t]  #convert list of tubles coming from SQL to list
          # print(emails)
          # print(len(emails))
          for x in range(0,len(emails)):
            if emails[x]is None:

              pass
            else:
              emails1.append(emails[x])
          # print(emails1)
          # return render_template("RFQ.html",username=username,supplier=supplier,final_emails=final_emails) 
          
    

          if len(emails1)==0:

            print("final email=0")
            flash('No emails found for this supplier, please update the database', "error")
            return render_template("RFQ.html",username=username,supplier=supplier,final_emails=final_emails)  
          
        # print(emails1)
        emails1=[string.replace("'","") for string in emails1]
        # print(emails1)
        emails1=[string.strip() for string in emails1]
        # print(emails1)

        
      
            
      
      else:
          print("not excel")
          flash('the file selected is not Excel, please recheck', "error")
          return render_template("RFQ.html",username=username,supplier=supplier,final_emails=final_emails) 
      
      
        

        # 

        #create PDF object
 
      pdf=PDF(inquiry_number,No_of_items,petra_codes,desc,qty,unit,suppliers1)
      pdf.alias_nb_pages()
      #set auto page break
      pdf.set_auto_page_break(auto=True,margin=3)
      #add page
      pdf.add_page()

      ###########################
      
 
      pdf.ln(5)
      # pdf.accept_page_break()
        # Select font
      pdf.set_font('Arial', 'B', 12)
      #  title
      pdf.cell(190, 10, 'Request for quotation',border=False, ln=1, align='C')
      # Line break
      pdf.ln(2)
      pdf.set_font('Arial', '', 10)
      pdf.multi_cell(w=150,h= 4,txt= "Dear Sir/Madam\nKindly provide us your best price and delivery date for below items:",border=0, align='L')
      pdf.ln(3)
    

      pdf.set_font('Arial', 'B', 12)
      pdf.cell(0, 0,txt = '---------------------------------------------------------------------------------------------------------------------------------------', ln = 1, align = 'L',border =0)
      pdf.cell(10, 8,txt = 'Item', ln = 0, align = 'C',border =0)
      pdf.cell(30, 8,txt = 'Code', ln = 0, align = 'C',border =0)
      pdf.cell(120, 8,txt = 'Description', ln = 0, align = 'C',border =0)
      pdf.cell(18, 8,txt = 'QTY', ln = 0, align = 'C',border =0)
      pdf.cell(15, 8,txt = 'UOM', ln = 1, align = 'C',border =0)
      pdf.cell(0, 0,txt = '---------------------------------------------------------------------------------------------------------------------------------------', ln = 1, align = 'L',border =0)
      pdf.set_font('Arial', '', 10)
      base_Line_height=10
      
    
      df = pd.DataFrame({'Item':No_of_items,'Code': petra_codes,'Description':desc,'QTY':qty,'UOM':unit})
      # print(df)
      print(len(df))
      for i in range(0,len(No_of_items)):
        # print(f"{df['Item'][i]}")
        pdf.cell(10, base_Line_height,txt=f"{df['Item'][i]}", ln = 0, align = 'C',border=0)
        pdf.cell(30, base_Line_height,txt = f"{df['Code'][i]}", ln = 0, align = 'C',border=0)
        y=pdf.get_y()
        x=pdf.get_x()
        pdf.multi_cell(w=120,h=6,txt= f"{df['Description'][i]}",border=0, align='L')
        y1=pdf.get_y()
        x1=pdf.get_x()
        pdf.set_xy(x+120,y)
        pdf.cell(18, base_Line_height,txt = f"{df['QTY'][i]}", ln = 0, align = 'C',border=0)
        pdf.cell(15, base_Line_height,txt = f"{df['UOM'][i]}", ln = 1, align = 'C',border=0)
        pdf.set_xy(x1,y1+1)
        pdf.cell(0, 0,txt = '------------------------------------------------------------------------------------------------------------------------------------------------------------------', ln = 1, align = 'L',border =0)

    
      
      #  #### export pdf file
      pdf.output(f"Z:/M.HAMMAD/RFQs/RFQ#{inquiry_number}.pdf")
      
 
    #### send the inquiry email
      mail_RFQ(emails1,f"Z:/M.HAMMAD/RFQs/RFQ#{inquiry_number}.pdf",inquiry_number)
      return render_template("RFQ.html",username=username,supplier=supplier,final_emails=final_emails)  
      
    
  else:
    supplier=[]
    conn = pyodbc.connect('Driver={SQL Server Native Client 11.0};'
                      'Server=PEEDM-HAMAD;'
                      'Database=usersDB;'
                      'Trusted_Connection=yes;')
    cursor=conn.cursor()
    
    query=f"SELECT Supplier FROM suppliers"
    rows=cursor.execute(query)
    rows=rows.fetchall()
    # conn.commit()
    # conn.close()
    if rows:
      
      for row in range (0,len(rows)):
        
        supplier.append(rows[row]) 
      supplier = [item for t in supplier for item in t]  #convert list of tubles coming from SQL to list
 
    return render_template("RFQ.html",username=username,supplier=supplier)


    