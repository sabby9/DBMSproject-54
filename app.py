from unittest import result
from flask import Flask, render_template, url_for, session, request, redirect
from flask_sqlalchemy import SQLAlchemy
import mysql.connector as mysql
from datetime import datetime
from werkzeug.datastructures import MultiDict

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from datetime import date

class RegisterForm(FlaskForm):
    firstname= StringField(label='firstname')
    lastname= StringField(label='lastname')
    email= StringField(label= 'Email') #abhi ke liye assume name type hai
    password= PasswordField(label= 'password')
    submit=SubmitField(label='sign up')

class LoginForm(FlaskForm):
    email =StringField(label= 'email')
    password=PasswordField(label= 'Password')
    submit= SubmitField(label='Login')

db= mysql.connect(host="localhost", user="root", passwd= "shani2130", database="bakery") #get that re named and ask passwd
#\connect root@localhost:3306. pwd: shani2130
mycursor= db.cursor()
#print(db)

app = Flask(__name__)
app.secret_key = "bakery"

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/login_page", methods= ['POST', 'GET'])
def login_page():
    if(request.method == "GET"):
         return render_template('login_page.html')
    else: 
        firstname= request.form['fname']
        password= request.form['password']
        query= f"SELECT * FROM customer WHERE first_name ='{firstname}';" and f"SELECT * FROM customer WHERE password='{password}';"
        mycursor.execute(query)
        records = mycursor.fetchall()
        if(len(records)==0):
            return redirect(url_for('home'))
        elif(len(records)==1):
             session.permanent = True
             session["user"] =records[0]
             temp = session["user"]
             print(temp)
             print(temp[0])
             return redirect(url_for('customer'))

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login_page"))

@app.route("/login_page_admin", methods= ['POST', 'GET']) #iako vo form wala thik karna hai aa
def login_page_admin():
    if(request.method == "GET"):
         return render_template('login_admin.html')
    else: 
        username= request.form['fname']
        password= request.form['password']
        query= f"SELECT * FROM admin WHERE username ='{username}';" and f"SELECT * FROM admin WHERE password='{password}';"
        mycursor.execute(query)
        records = mycursor.fetchall() #this is list of list 
        if(len(records)==0):
            return redirect(url_for('login_page_admin'))
        elif(len(records)==1):
                        
            if(username == "admin1" or username == "admin2" or username == "admin3" ):
                return redirect(url_for('distributor'))
                 
            elif(username == "admin4" or username == "admin5" or username == "admin6"):
                return redirect(url_for('admin_inventory_manager'))
            elif(username == "admin7" or username == "admin8" or username == "admin9"):
                return redirect(url_for('admin_consultant'))
            elif(username == "admin10"):    
                return redirect(url_for('admin_customer_care'))


            

@app.route("/admin_customer_care", methods= ['POST', 'GET'])
def admin_customer_care():
    return render_template("customer_care.html")

@app.route("/admin_customer_care/view_customers", methods= ['POST', 'GET'])
def admin_customer_care_view_customers():
    q= f"Select first_name , last_name,  house_no, street, city ,zip , dob from customer;"
    mycursor.execute(q)
    item = mycursor.fetchall()
    return render_template("cc_view_customer.html", data= item)
    

@app.route("/admin_customer_care/unpaid_orders", methods= ['POST', 'GET'])
def admin_customer_care_unpaid_orders():
    q=f"select distinct first_name, last_name from customer natural join (select customer_id from cart where date_of_delivery < curdate() and payment_status = 0) as t;"
    mycursor.execute(q)
    item = mycursor.fetchall()
    return render_template("cc_unpaid_orders.html", data= item)

@app.route("/admin_inventory_manager", methods= ['POST', 'GET'])
def admin_inventory_manager():
    return render_template("inv.html")

@app.route("/admin_consultant", methods= ['POST', 'GET'])
def admin_consultant():
     if(request.method == "GET"):
            q=f"select  product_id,  product_name, average_rating from product natural join (select product_id, average_rating from (select product_id, avg(rating_given) as average_rating from rating group by product_id) as t where average_rating < 2) as tt;"
            mycursor.execute(q)
            item = mycursor.fetchall()
            return render_template("consultant.html", data= item)
 
       
     else:
        pid = request.form['pid']
        print(pid)
        q=f"DELETE FROM product p WHERE p.product_id='{pid}';"
        mycursor.execute(q)
        db.commit()
        return(redirect("admin_consultant"))   
    
    

@app.route("/admin_distributor", methods= ['POST', 'GET'])
def admin_distributor():
    return render_template('dist.html')

@app.route("/customer", methods= ['POST', 'GET'])
def customer():
    if("user" in session):
        return render_template("customer.html") 
    return "<p>This is distr's</p>"

@app.route("/customer/profile", methods= ['POST', 'GET'])
def customer_profile():
    if("user" in session):
        user_cookie= session["user"][0] #i think this is customer id and ask about log out coz vo logged in rehta hai last person ka ??
        print("c id in profile=" + str(user_cookie))
        query= f"Select first_name , last_name,  house_no, street, city ,zip , dob from customer where customer_id = '{user_cookie}';"
        mycursor.execute(query)
        item = mycursor.fetchall()
        d = [["first name: "], ["last name: "], ["House number: "], ["Street:"], ["City:"], ["zip:"], ["DOB:"]]
        for i in range(len(item[0])):
            d[i]. append(item[0][i]) 

       
        return render_template("customer_profile.html" , data=d) 


@app.route("/customer/past_orders", methods= ['POST', 'GET'])
def customer_past_orders():
    if(request.method == "GET"):
        if("user" in session):
            user_cookie= session["user"][0] #i think this is pass??
            print("c id=" + str(user_cookie))
            query= f"Select order_id, payment_status, date_of_delivery from customer c, cart cr where c.customer_id = '{user_cookie}' and c.customer_id = cr.customer_id;"
            mycursor.execute(query)
            item = mycursor.fetchall() #((1,2,3) , (1,2,3))
            d = [ ]
            for i in range(len(item)):
                l= item[i]
                a= ["  order id: " , str(l[0]) ]
                b=  ["  payment status:" , str(l[1]) ]
                c= ["  date of delivery" ,  str(l[2]) ]
                d.append(a)
                d.append(b)
                d.append(c)
                
        
        return render_template('past_order.html', data = d)

    else:
        orderid= request.form['orderid']
        print(orderid)
        if("user" in session):
            user_cookie= session["user"][0] #i think this is customer id and ask about log out coz vo logged in rehta hai last person ka ??
            query= f"Select product_name, quantity, c.cost from product p, cart_item c where c.cid = '{user_cookie}' and c.oid = '{orderid}' and p.product_id= c.fid;"
            mycursor.execute(query)
            item = mycursor.fetchall() #((1,2,3) , (1,2,3))
            d= []
            for i in range(len(item)):
                l= item[i]
                a= ["  name : " , str(l[0]) ]
                b=  ["  quantity :" , str(l[1]) ]
                c= ["  cost: " ,  str(l[2]) ]
                d.append(a)
                d.append(b)
                d.append(c)

        return render_template('past_order_details.html', data= d)



@app.route("/customer/place_order", methods= ['POST', 'GET'])
def customer_place_order():
    if(request.method == "GET"):
        if("user" in session):
                user_cookie= session["user"][0] #i think this is customer id and ask about log out coz vo logged in rehta hai last person ka ??
                query= f"Select product_id, product_name, cost, manufacture_date from product p;"
                mycursor.execute(query)
                item = mycursor.fetchall() #((1,2,3) , (1,2,3))
                return render_template('place_order.html', data = item)
    else:
            quan= request.form
            d=[]
            l =quan.getlist("quantity")
            pt=quan.get("payment_type")
            print(pt)
            for i in range(len(l)):
                if l[i] != '0':
                
                    o= [i+1, int(l[i])]
                    d.append(o)
            print(d)
            query1= f"SELECT order_id FROM cart;"
            mycursor.execute(query1)
            records = mycursor.fetchall() #this is list of list 
            
            x= len(records) + 1
            print("value of x="+ str(x))
            user_cookie= session["user"][0]
            pp= []
            for i in range(len(d)):
                pid= d[i][0]
                query2= f"SELECT cost from product p where p.product_id= '{pid}';"
                mycursor.execute(query2)
                pro = mycursor.fetchall()
                tup= pro[0]
                pp.append(int(tup[0]))
            
            print(pp)       #now d has like pid, quantity pair and pp has cost of each pid
            
            #calculate total price
            total_price=0
            for u in range(len(pp)):
                total_price = total_price + pp[u]*d[u][1]
            print("total price=" + str(total_price))

            if(total_price>=5000 and pt=="COD"):
                return redirect(url_for('customer_place_order'))
            #if time left isko standard date wala karna hai
            dt = datetime.now()
            dt = dt.strftime("%Y-%m-%d")
            print(dt)

            if(total_price>5000):
                pay=1
            else:    
                if(x%2==0):
                    pay=1
                else:
                    pay=0    
                       
            q3 = f"INSERT INTO cart(order_id, customer_id, payment_status, date_of_delivery, total_price) VALUES('{x}', '{user_cookie}', {pay}, '{dt}', {str(total_price)});"
            print(str(x) + str(user_cookie))
            mycursor.execute(q3)
            success = mycursor.fetchall() 
            db.commit()

         
            for i in range(len(d)):
                print(str(x) + " " + str(user_cookie) + " " + str(d[i][0]))
                q4=f"INSERT INTO cart_item(oid, cid, fid, quantity, cost) VALUES('{x}', '{user_cookie}', '{d[i][0]}', '{d[i][1]}', {str(pp[i])});"
              
                mycursor.execute(q4)
                db.commit()

           # isko thik karna hai 

            # reduce the remaning quantity in db:
            for i in range(len(d)):
                pid= d[i][0]
               
                query2= f"SELECT remaining_quatity from product p where p.product_id= '{pid}';"
                mycursor.execute(query2)
                pro = mycursor.fetchall()
                tup= pro[0]
                print(tup)
                s =int(tup[0])
                print(s)
                s= s- d[i][1]
                quan= str(s)
                
                query3= f"UPDATE product SET remaining_quatity = '{s}' WHERE product_id = '{pid}';"
                mycursor.execute(query3)
                db.commit()
            return (render_template('order_success.html'))

@app.route("/customer/most_liked", methods= ['POST', 'GET'])
def most_liked():
    if("user" in session):
        user_cookie= session["user"][0] #i think this is customer id and ask about log out coz vo logged in rehta hai last person ka ??
        print("c id in profile=" + str(user_cookie))
        
        query= f"select customer_id, first_name, last_name product_id, product_name from customer natural join (select product_id, product_name from product natural join (select product_id from (select product_id, customer_id, avg(rating_given) over(partition by customer_id) as avg_rating from rating) as t where avg_rating > 4) as tt) as ttt where customer_id = '{user_cookie}';"
        mycursor.execute(query)
        item = mycursor.fetchall()
           
        return render_template("mostliked.html" , data=item) 

@app.route("/customer/cart", methods= ['POST', 'GET'])
def customer_cart():
    return(render_template('index.html'))

@app.route("/sign_up_page", methods= ['POST', 'GET'])
def sign_up_page():
    form= RegisterForm()
    if form.validate_on_submit():
        return redirect(url_for('login_page'))
      
    return render_template('sign_up_page.html', form= form)

@app.route("/products", methods= ['POST', 'GET'])
def products():
    if(request.method== 'GET'):
       print("")
    return render_template('products.html')


if __name__=="__main__":
    app.run(debug=True)                                                                   
