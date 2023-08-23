import MySQLdb
from flask import Flask , render_template, request, redirect, session, url_for
from flask_mysqldb import MySQL
app = Flask(__name__)
app.secret_key = 'rs'
app.config["MYSQL_HOST"]="localhost"
app.config["MYSQL_USER"]="root"
app.config["MYSQL_PASSWORD"]=""
app.config["MYSQL_DB"]="nammakada"
mysql=MySQL(app)

@app.route('/')
def home():
   return render_template("index.html")


@app.route('/adminlogin')
def adminlogin():
   mesage = ''
   if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form.get("username")
        password = request.form.get("password")
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM admin WHERE admin = % s AND password = % s', (username, password))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            return redirect(url_for("admin"))
        else:
            mesage = 'Please enter correct email / password !'
   return render_template('adminlogin.html')

@app.route('/admin',methods=['GET','POST'])
def admin():
   cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
   cursor.execute("SELECT * FROM company")
   res = cursor.fetchall()
   return render_template("adminpage.html",datas=res)

@app.route('/addcompany',methods=['GET','POST'])
def addcompany():
          if request.method == 'POST':
            name = request.form.get("company")
            password = request.form.get("password")
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('insert into company(company_name,password) values(%s,%s)',(name,password))
            mysql.connection.commit()
            mysql.connection.close()
            return redirect(url_for("admin"))
          return render_template('addcompany.html')

@app.route('/companylogin', methods =['GET', 'POST'])
def login():
    mesage = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form.get("username")
        password = request.form.get("password")
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM company WHERE company_name = % s AND password = % s', (username, password))
        user = cursor.fetchone()
        if user:
            #session['loggedin'] = True
            #app.config["company"] = username
            return redirect(url_for("company",var=username))
        else:
            mesage = 'Please enter correct email / password !'
    return render_template('companylogin.html')

@app.route('/company',methods=['GET','POST'])
def company():
   cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
   cursor.execute("SELECT * FROM company WHERE company_name = 'ABC'")
   res = cursor.fetchall()
   return render_template("company.html",datas=res)

@app.route('/addcash',methods=['GET','POST'])
def addcash():
      mesage = ''
      if request.method == 'POST' and 'company' in request.form and 'amount' in request.form:
          name = request.form.get("company")
          amount = request.form.get("amount")
          cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
          cursor.execute('UPDATE company SET cash_balance=% s where company_name=% s',(amount,name))
          mysql.connection.commit()
          mysql.connection.close()
          return redirect(url_for("company"))
      return render_template('addcash.html')

@app.route('/stack')
def stack():
   cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
   cursor.execute("Select cash_balance from company where company_name = 'ABC'")
   bal = cursor.fetchone()
   cursor.execute('SELECT * FROM items')
   res = cursor.fetchall()
   return render_template("stack.html",datas=res,cash = bal)

@app.route('/purchase',methods=['GET','POST'])
def purchase():
    if request.method =='POST':
        ID = request.form.get("ID")
        Item = request.form.get("item")
        Qty = request.form.get("qty")
        Rate = request.form.get("rate")
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO purchase(Item_ID,Item_Name,Qty,Rate) VALUES(% s,% s,% s,% s)',(ID,Item,Qty,Rate))
        mysql.connection.commit()
        cursor.execute('insert into items(Item_ID,Item_Name,Rate,Quantity) values(%s,%s,%s,%s) on duplicate key update items.Quantity = items.Quantity + %s',(ID,Item,Rate,Qty,Qty))
        mysql.connection.commit()
        amt = int(Qty)*int(Rate)
        #company = app.config.get("company")
        # cursor.execute("select company_name from company where company_name= 'ABC'")
        # cmp = cursor.fetchone()
        cursor.execute('UPDATE company SET cash_balance = cash_balance - %d where company_name = "ABC"'% (int(amt)))
        mysql.connection.commit()
        mysql.connection.close()
        return redirect(url_for("purchaselist"))
    return render_template("purchase.html")


@app.route('/purchaselist',methods=['GET','POST'])
def purchaselist():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('UPDATE purchase SET Amount = Qty * Rate')
    mysql.connection.commit()
    cursor.execute("Select cash_balance from company where company_name = 'ABC'")
    bal = cursor.fetchone()
    cursor.execute('SELECT * FROM purchase')
    res = cursor.fetchall()
    return render_template("purchaselist.html",datas=res,cash=bal)

@app.route('/saleslist',methods=['GET','POST'])
def saleslist():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("Select cash_balance from company where company_name = 'ABC'")
    bal = cursor.fetchone()
    cursor.execute('SELECT * FROM items')
    res = cursor.fetchall()
    return render_template("saleslist.html",datas=res,cash=bal)

@app.route('/sale',methods=['GET','POST'])
def sale():
      mesage = ''
      if request.method == 'POST':
          item = request.form.get("item")
          qty = request.form.get("qty")
          rate = request.form.get("rate")
          cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
          cursor.execute('UPDATE items SET Quantity= Quantity - %s where Item_ID= %s',(qty,item))
          mysql.connection.commit()
          cursor.execute('INSERT into sales(Item_ID,Qty,Rate) values(%s,%s,%s)',(item,qty,rate))
          mysql.connection.commit()
          amt = int(qty)*int(rate)
          #company = app.config.get("company")
          cursor.execute('UPDATE company SET cash_balance = cash_balance + %d where company_name = "ABC"'% (int(amt)))
          mysql.connection.commit()
          mysql.connection.close()
          return redirect(url_for("invoice"))
      return render_template('sale.html')

@app.route('/invoice',methods=['GET','POST'])
def invoice():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('UPDATE sales SET Amount = Qty * Rate')
    mysql.connection.commit()
    cursor.execute("Select cash_balance from company where company_name = 'ABC'")
    bal = cursor.fetchone()
    cursor.execute('SELECT * FROM sales')
    res = cursor.fetchall()
    return render_template("invoice.html",datas=res,cash=bal)

@app.route('/editrate',methods=['GET','POST'])
def editrate():
      mesage = ''
      if request.method == 'POST':
          id = request.form.get("id")
          rate = request.form.get("rate")
          cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
          cursor.execute('UPDATE items SET Rate=% s where Item_ID=% s',(rate,id))
          mysql.connection.commit()
          mysql.connection.close()
          return redirect(url_for("stack"))
      return render_template('editrate.html')


if __name__ == '__main__':
   app.run(debug=True)