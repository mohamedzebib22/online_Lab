from email.message import EmailMessage
from functools import partial
import win32com.client as win
from kivymd.uix.pickers import MDDatePicker
from email.utils import formataddr
import smtplib
import ssl
from kivy.core.text import LabelBase
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.textfield import MDTextField
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from kivy.uix.behaviors import FocusBehavior
from kivy.metrics import dp
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.card import MDCard
from kivy.uix.image import Image
from kivymd.uix.button import MDIconButton,MDRaisedButton
from kivy.uix.screenmanager import ScreenManager , Screen 
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.utils import platform
from kivy.core.window import Window
import requests
import firebase_admin
from firebase_admin import credentials, auth ,db,firestore
from kivymd.uix.dialog import MDDialog
from kivymd.toast import toast
import pyrebase
from kivy.uix.widget import Widget
from plyer import filechooser,notification
from kivy.properties import ObjectProperty
from kivymd.uix.label import MDLabel
import uuid
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from plyer import call
import subprocess
import webbrowser
import platform as plat
Window.size=(330,590)



config = {
    "apiKey": "AIzaSyDyuEohOlFGGJDDsSAlh9rvjZSZ8shXEig",
    "authDomain": "medicalapp-73d41.firebaseapp.com",
    "databaseURL": "https://medicalapp-73d41-default-rtdb.firebaseio.com/",
    "projectId": "medicalapp-73d41",
    "storageBucket": "medicalapp-73d41.appspot.com",
    "messagingSenderId": "565079436237",
    "appId": "1:565079436237:web:5ac629e5d123113ed3f284",
    "measurementId": "G-1F5LN1DJHW",
    "serviceAccount":"medicalapp-73d41-firebase-adminsdk-8gfnf-c37d4105cb.json"
}

cred = credentials.Certificate("medicalapp-73d41-firebase-adminsdk-8gfnf-fd33dcdc83.json")
firebase_admin.initialize_app(cred,{"databaseURL": "https://medicalapp-73d41-default-rtdb.firebaseio.com/"})
ref = db.reference('/Analysis')
firestoree = firestore.client()
firebase = pyrebase.initialize_app(config)
db = firebase.database()
auth=firebase.auth()


class NavBar(FocusBehavior ,MDFloatLayout):
    pass

class About_App(Screen):
    pass
class Update(Screen):
    def on_pre_enter(self):
        # حذف المنتجات المعروضة حاليًا قبل عرض منتجات المعمل الجديدة
        self.ids.update_grid.clear_widgets()
        # عرض قائمة المعامل
        self.save_changes()
    def save_changes(self):
        update_grid = self.ids.update_grid
        update_grid.clear_widgets()
        try:
            email = self.manager.get_screen('login_admin').email
             
            
            # جلب المنتجات المخزنة بناءً على عنوان البريد الإلكتروني
            user_products = firestoree.collection('users').document(email).collection('products').get()
            for doc in user_products:
                data = doc.to_dict()
                analysis_name = data.get("analysis_name", "")
                lab_price = str(data.get("price", ""))
                
                card_layout = GridLayout(padding=8, spacing=8, cols=2) 
                
                # إضافة عنصر Label لعرض اسم التحليل
                analysis_label = MDLabel(text=f"Analysis Name: {analysis_name}",id="analysis_label",theme_text_color="Custom",text_color="red" ,font_style="Button")

                card_layout.add_widget(analysis_label)
                
                # إضافة عنصر Label لعرض السعر
                price_label = MDLabel(text=f"Price: {lab_price}",id="price_label",theme_text_color="Custom",text_color="red" ,font_style="Button")
                card_layout.add_widget(price_label)
                
                # إضافة عنصر TextField لإدخال التحديث المحتمل لاسم التحليل
                new_name = MDTextField()
                card_layout.add_widget(new_name)
                
                # إضافة عنصر TextField لإدخال التحديث المحتمل للسعر
                new_price = MDTextField()
                card_layout.add_widget(new_price)
                
                # زر تحديث بيانات المنتج
                update_button = MDRaisedButton(text="Update",md_bg_color="green")
                # يتم ربط الزر بالدالة المسؤولة عن تحديث البيانات وإرسال القيم الجديدة
                update_button.bind(on_press=lambda instance, name=new_name, price=new_price, document_id=doc.id: self.update_product(email, name.text, price.text, document_id))
                card_layout.add_widget(update_button)
                
                # زر حذف المنتج
                delete_button = MDRaisedButton(text="Delete",md_bg_color="red")
                delete_button.bind(on_press=lambda instance, document_id=doc.id: self.delete_product(email, document_id))
                card_layout.add_widget(delete_button)
                # إضافة الـ GridLayout إلى الشبكة
                card = MDCard(size_hint_y=None, height=dp(200), padding=dp(10), md_bg_color="gold", radius=[40, ])
                card.add_widget(card_layout)
                update_grid.add_widget(card)
                
                # 
                
        except Exception as error:
             
            self.show_error_dialog("Please check data")
    def show_error_dialog(self, error_message):
        dialog = MDDialog(
            title="ُERROR",
            text=error_message,
            size_hint=(0.7, 0.3)
        )
        dialog.open()
    def update_product(self, email, analysis_name, price, document_id):
        try:

            # استعلام للحصول على الوثيقة المحددة بناءً على معرف الوثيقة
            product_ref = firestoree.collection('users').document(email).collection('products').document(document_id)
            
            # تحديث الوثيقة في Firestore
            product_ref.update({"analysis_name": analysis_name, "price": price})
            
             
            speaker =win.Dispatch("SAPI.SPvoice")
            speaker.Speak("Product updated successfully")
            
        except Exception as error:
            speaker =win.Dispatch("SAPI.SPvoice")
            speaker.Speak("please check data")
             
    def delete_product(self, email, document_id):
        try:
            # الحصول على مرجع الوثيقة المطلوبة
            product_ref = firestoree.collection('users').document(email).collection('products').document(document_id)
            
            # حذف الوثيقة من Firestore
            product_ref.delete()
             
            speaker =win.Dispatch("SAPI.SPvoice")
            speaker.Speak("Product delete successfully")
            # إخفاء الكارد عن طريق إزالته من الشاشة
            
        except Exception as error:
            speaker =win.Dispatch("SAPI.SPvoice")
            speaker.Speak("please check data")
             
            
    def search_update(self):
        search_update = self.ids.search_update.text.strip()  # الحصول على النص المدخل في حقل البحث وحذف الفراغات الزائدة
        email = self.manager.get_screen('login_admin').email
        # تحديث عرض الصفحة فقط إذا كان هناك نص مدخل في حقل البحث
        if search_update:
            update_grid = self.ids.update_grid
            update_grid.clear_widgets()  # تفريغ العناصر القديمة

            # جلب جميع الوثائق التي تطابق البحث
            admin_docs = firestoree.collection('users').document(email).collection('products').get()
            
            for doc in admin_docs:
                data = doc.to_dict()
                analysis_name = data.get("analysis_name", "")
                # التحقق مما إذا كان عنوان المعمل يحتوي على النص المطلوب
                if search_update in analysis_name:                    
                    analysis_name = data.get("analysis_name", "")
                    lab_price = str(data.get("price", ""))

                    card_layout = GridLayout(padding=10, spacing=10, cols=2)
                    #card_layout.add_widget(MDLabel(text=f"Lab Name: {lab_name}"))
                    card_layout.add_widget(MDLabel(text=f"Name: {analysis_name}",theme_text_color="Custom",text_color="green" ,font_style="Button"))
                    card_layout.add_widget(MDLabel(text=f"Price: {lab_price}",theme_text_color="Custom",text_color="red" ,font_style="Button"))
                    
                    # إضافة عنصر TextField لإدخال التحديث المحتمل لاسم التحليل
                    new_name = MDTextField()
                    card_layout.add_widget(new_name)
                    
                    # إضافة عنصر TextField لإدخال التحديث المحتمل للسعر
                    new_price = MDTextField()
                    card_layout.add_widget(new_price)
                    
                    # زر تحديث بيانات المنتج
                    update_button = MDRaisedButton(text="Update",md_bg_color="green")
                    # يتم ربط الزر بالدالة المسؤولة عن تحديث البيانات وإرسال القيم الجديدة
                    update_button.bind(on_press=lambda instance, name=new_name, price=new_price, document_id=doc.id: self.update_product(email, name.text, price.text, document_id))

                    card_layout.add_widget(update_button)
                    
                    # زر حذف المنتج
                    delete_button = MDRaisedButton(text="Delete",md_bg_color="red")
                    delete_button.bind(on_press=lambda instance, document_id=doc.id: self.delete_product(email, document_id))
                    card_layout.add_widget(delete_button)
                        
                    card = MDCard(size_hint_y=None, height=dp(200), padding=dp(10), md_bg_color="gold", radius=[40, ])
                    card.add_widget(card_layout)
                    update_grid.add_widget(card)
    
class Forgot_password_admin(Screen):
    def reset_password_admin(self):
        email = self.ids.email_input_admin.text
        lab_name=self.ids.lab_name_admin.text
        phone_lab = self.ids.phone_input_admin.text
        new_password = self.ids.new_password_input_admin.text
        try:
            
            if email and new_password and phone_lab and lab_name:
                user_ref = firestoree.collection("Admin_Email").document(email)
                user_data = user_ref.get().to_dict()
                if user_data and user_data.get('phone_lab') == phone_lab and user_data.get('lab_name') == lab_name :
                    # Update password if email and phone match
                    user_ref.update({'password': new_password})
                     
                    self.manager.current = "login_user"
                else:
                    self.show_error_dialog('please check data')
        except Exception as Er:
             
            self.show_error_dialog('please check data') 
    def show_error_dialog(self, error_message):
        dialog = MDDialog(
            title="ُERROR",
            text=error_message,
            size_hint=(0.7, 0.3)
        )
        dialog.open()
class Forgot_password(Screen):

    def reset_password(self):
        email = self.ids.email_input.text
        date=self.ids.date.text
        phone = self.ids.phone_input.text
        new_password = self.ids.new_password_input.text
        try:
            
            if email and new_password and phone and date:
                user_ref = firestoree.collection("user_email").document(email)
                user_data = user_ref.get().to_dict()
                if user_data and user_data.get('phone') == phone and user_data.get('date') == date :
                    # Update password if email and phone match
                    user_ref.update({'password': new_password})
                     
                    self.manager.current = "login_user"
                else:
                     self.show_error_dialog('please check data')
        except Exception as Er:
             
            self.show_error_dialog('please check data')
    def show_error_dialog(self, error_message):
        dialog = MDDialog(
            title="ُERROR",
            text=error_message,
            size_hint=(0.7, 0.3)
        )
        dialog.open()
    
        
class Show_Analysis(Screen):
   
    def show_data(self, lab_name):
        analysis_grid = self.ids.analysis_grid
        analysis_grid.clear_widgets()
        admin_docs = firestoree.collection("Admin_Email").get()
        for doc in admin_docs:
            admin_data = doc.to_dict()
            email = admin_data.get("email")
            docs = firestoree.collection("users").document(email).collection("products").where("lab_name", "==", lab_name).get()
            for doc in docs:
                data = doc.to_dict()
                lab_name=data.get("lab_name", "")
                lab_address = data.get("lab_address", "")
                phone_lab = data.get("phone_lab", "")
                analysis_name = data.get("analysis_name", "")
                lab_price = str(data.get("price", ""))
              #  photo = data.get("photo", "")
                payment=data.get("paypal_email","")
                
                card_layout = GridLayout(padding=2, spacing=2, cols=2)
                card_layout.add_widget(MDLabel(text=f"Name: {analysis_name}" ,theme_text_color="Custom",text_color="red" ,font_style="Button"))
               # card_layout.add_widget(Image(source=photo))
                card_layout.add_widget(MDLabel(text=f"Price: {lab_price}" ,theme_text_color="Custom",text_color="blue"  ,font_style="Body1"))
                card_layout.add_widget(MDLabel(text=f"Address: {lab_address}",theme_text_color="Custom",text_color="brown"  , font_style="Button"))
                
                #card_layout.add_widget(MDLabel(text=f"Lab Name: {lab_name}"))
                #card_layout.add_widget(MDLabel(text=f"Phone: {phone_lab}"))
                card_layout.add_widget(MDLabel(text="  "))
                

                whatsapp_button = MDIconButton(icon="whatsapp", font_size=20, md_bg_color="green")
                whatsapp_button.bind(on_release=lambda button, phone_number=phone_lab: self.contact_whatsapp(phone_number))
                card_layout.add_widget(whatsapp_button)

                phone_button = MDIconButton(icon="phone", font_size=20, md_bg_color="green")
                phone_button.bind(on_release=lambda button, phone_number=phone_lab: self.call_number(phone_number))
                card_layout.add_widget(phone_button)
                
                # إضافة زر للإبلاغ
                report_button = MDIconButton(icon="alert-circle", size_hint_y=None, height=50 ,md_bg_color="red")
                report_button.bind(on_release=lambda instance, name=analysis_name: self.send_email_popup(name))
                card_layout.add_widget(report_button)
                
                pay_button = MDRaisedButton(text="pay", size_hint_y=None, height=50)
                pay_button.bind(on_release=lambda instance, price=lab_price , mail=payment :self.create_paypal_payment(mail, price))
                card_layout.add_widget(pay_button)
                
                card = MDCard(size_hint_y=None, height=dp(200), padding=dp(10), md_bg_color="gold", radius=[40, ])
                card.add_widget(card_layout)
                analysis_grid.add_widget(card)
    
    def get_dollar_rate(self):
        try:
            response = requests.get('https://api.exchangerate-api.com/v4/latest/USD')
            data = response.json()
            dollar_rate = data['rates']['EGP']
            return dollar_rate
        except Exception as e:
             
            return None
        
                
    def create_paypal_payment(self,payment, lab_price):
        dollar_rate = self.get_dollar_rate()
        if dollar_rate is not None:
            lab_price_float = float(lab_price)
            lab_price_usd = lab_price_float / dollar_rate 
            paypal_url = f"https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business={payment}&amount={lab_price_usd}&currency_code=USD"
             
            webbrowser.open(paypal_url)
            return paypal_url
        
    def send_email_popup(self, analysis_name):
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        message_input = MDTextField(multiline=True ,id="hi")
        popup_layout.add_widget(message_input)

        send_button = MDRaisedButton(text='Send', size_hint_y=None, height=50)
        send_button.bind(on_release=lambda instance: self.send_email(message_input.text,popup))
        popup_layout.add_widget(send_button)

        popup = Popup(title='Send Email', content=popup_layout, size_hint=(None, None), size=(400, 200))
        popup.open()
    def send_email(self , message, popup):
        admin_docs = firestoree.collection("user_email").get()
        for doc in admin_docs:
            admin_data = doc.to_dict()
            name = admin_data.get("user_name")
            email_user = admin_data.get("email")
            
            
                    
            email = "mohamedzebib22@gmail.com"
            password = "llkfqplyizmgwjgg"
                    
            msg = EmailMessage()
            msg["Subject"] = "New Contact From Enquiry!"
            msg["To"] = "mohamedzebib22@gmail.com"
            msg["From"] = formataddr((name, email_user))

            msg.set_content(f"Hi, my name is {name}. \n{message}")
            try:
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    smtp.login(email, password)
                    smtp.send_message(msg)
                 
                popup.dismiss()
            except Exception as e:
                 
                self.show_error_dialog("please check data")
                
          
    def call_search_product(self):
        search_text = self.ids.search_field2.text.strip()  # الحصول على النص المدخل في حقل البحث وحذف الفراغات الزائدة

        # تحديث عرض الصفحة فقط إذا كان هناك نص مدخل في حقل البحث
        if search_text:
            analysis_grid = self.ids.analysis_grid
            analysis_grid.clear_widgets()  # تفريغ العناصر القديمة

            # جلب جميع الوثائق التي تطابق البحث
            admin_docs = firestoree.collection("Admin_Email").get()
            for doc in admin_docs:
                admin_data = doc.to_dict()
                email = admin_data.get("email")
                docs = firestoree.collection("users").document(email).collection("products").get()
                for doc in docs:
                    data = doc.to_dict()
                    analysis_name = data.get("analysis_name", "")
                    # التحقق مما إذا كان عنوان المعمل يحتوي على النص المطلوب
                    if search_text in analysis_name:
                        #lab_name = data.get("lab_name", "")
                        phone_lab = data.get("phone_lab", "")
                        analysis_name = data.get("analysis_name", "")
                        lab_price = str(data.get("price", ""))
                        photo = data.get("photo", "")
                        lab_address = data.get("lab_address", "")
                        payment=data.get("paypal_email","")

                        card_layout = GridLayout(padding=10, spacing=10, cols=2)
                        #card_layout.add_widget(MDLabel(text=f"Lab Name: {lab_name}"))
                        card_layout.add_widget(MDLabel(text=f"Name: {analysis_name}",theme_text_color="Custom",text_color="red" ,font_style="Button"))
                        card_layout.add_widget(MDLabel(text=f"Address: {lab_address}",theme_text_color="Custom",text_color="green" ,font_style="Button"))
                        card_layout.add_widget(MDLabel(text=f"Price: {lab_price}",theme_text_color="Custom",text_color="red" ,font_style="Button"))
                        card_layout.add_widget(MDLabel(text=f"Phone: {phone_lab}",theme_text_color="Custom",text_color="green" ,font_style="Button"))
                        
                        
                        

                        whatsapp_button = MDIconButton(icon="whatsapp", font_size=20, md_bg_color="teal")
                        whatsapp_button.bind(on_release=lambda button, phone_number=phone_lab: self.contact_whatsapp(phone_number))
                        card_layout.add_widget(whatsapp_button)

                        phone_button = MDIconButton(icon="phone", font_size=20, md_bg_color="teal")
                        phone_button.bind(on_release=lambda button, phone_number=phone_lab: self.call_number(phone_number))
                        card_layout.add_widget(phone_button)
                        
                        # إضافة زر للإبلاغ
                        report_button = MDIconButton(icon="alert-circle", size_hint_y=None, height=50 ,md_bg_color="red")
                        report_button.bind(on_release=lambda instance, name=analysis_name: self.send_email_popup(name))
                        card_layout.add_widget(report_button)
                        
                        pay_button = MDRaisedButton(text="pay", size_hint_y=None, height=50)
                        pay_button.bind(on_release=lambda instance, price=lab_price , mail=payment :self.create_paypal_payment(mail, price))
                        card_layout.add_widget(pay_button)

                        card = MDCard(size_hint_y=None, height=dp(200), padding=dp(10), md_bg_color="gold", radius=[40, ])
                        card.add_widget(card_layout)
                        analysis_grid.add_widget(card)
                        self.ids.search_field2.text = ""
                    
        
    def contact_whatsapp(self, phone_number):
        # تحقق من نوع النظام الأساسي
        system_platform = plat.system()
        
        # تنسيق رقم الهاتف
       
        formatted_phone_number = "+20" + phone_number
        
        # إعداد رابط واتساب بناءً على نوع النظام الأساسي
        if system_platform == "Windows":
            whatsapp_link = "https://wa.me/" + formatted_phone_number
        elif system_platform == "Darwin":  # macOS
            whatsapp_link = "https://api.whatsapp.com/send?phone=" + formatted_phone_number
        elif system_platform == "Linux":
            whatsapp_link = "https://wa.me/" + formatted_phone_number
        elif system_platform == "android":
            whatsapp_link = "https://wa.me/" + formatted_phone_number
        elif system_platform == "macosx":
            whatsapp_link = "https://api.whatsapp.com/send?phone=" + formatted_phone_number
        else:
            # Handle other platforms here
            return
        
        notification.notify(
            title='WhatsApp Link',
            message=whatsapp_link,
            app_name='Kivy App',
            app_icon=None,
        )
        # فتح رابط واتساب في المتصفح الافتراضي
        webbrowser.open(whatsapp_link)
         
        
    def call_number(self, phone_number):
        platform=plat.system()
        formatted_phone_number = "+20" + phone_number
        
        if platform == 'android' or platform == 'ios':
            webbrowser.open('tel://' + formatted_phone_number)
        elif platform == 'Windows':
             
            webbrowser.open('tel://' + formatted_phone_number)
        elif platform == 'Darwin':
            subprocess.call(['open', 'tel:' + formatted_phone_number])
        elif platform == 'Linux':
            phone = 'tel://' + formatted_phone_number
            webbrowser.open(phone)
        else:
            self.show_error_dialog('please check platform')
             
    def show_error_dialog(self, error_message):
        dialog = MDDialog(
            title="ُERROR",
            text=error_message,
            size_hint=(0.7, 0.3)
        )
        dialog.open()
class WhoAreYou(Screen):
    pass

class Lab(Screen,Widget):
   
    def file_chooser(self):
        filechooser.open_file(on_selection=self.selected)
    def selected(self,selection):
        self.parent.get_screen('laboratory').ids.img.source=selection[0] 
        
    user_data = {}  # تخزين بيانات المستخدم هنا

    def set_user_data(self, user_data):
        self.user_data = user_data
        if isinstance(user_data, dict):
            # تحقق من أن البيانات غير فارغة
            if 'lab_name' in user_data or 'phone_lab' in user_data or 'lab_address' in user_data :
                self.ids.lab_name.text = f"{user_data['lab_name']}"
                self.ids.phone_lab.text=f"{user_data['phone_lab']}"
                self.ids.lab_address.text=f"{user_data['lab_address']}"
            else:
                self.ids.lab_name.text = "Default Lab Name"  # تعيين قيمة افتراضية في حالة عدم وجود lab_name
        else:
            # في حالة كانت user_data قائمة، قد يتعين عليك التحقق من الفهرس المطلوب والتأكد من أن القائمة غير فارغة
            pass  # يمكنك القيام بالمنطق المناسب هنا
        #self.ids.lab_name.text = f"{[user_data]['lab_name']}"
        
        #self.ids.lab_address.text = f"{user_data['lab_name']}"
        #self.ids.phone_lab.text = f"{user_data['phone_lab']}"

    def storage_data(self):
        try:
           
            if isinstance(self.user_data, list):
                email = self.user_data[0].get("email")
            else:
                email = self.user_data.get("email")

            


             
            
            # التحقق من أن البيانات غير فارغة
            if not self.parent.get_screen('laboratory').ids.analysis_name.text or not float(self.parent.get_screen('laboratory').ids.lab_price.text) :
                self.show_error_dialog("PLease Enter Data")
            analysis_id = str(uuid.uuid4())
            data={
                "email": email,
                "lab_name":self.ids.lab_name.text ,
                "lab_address":self.parent.get_screen('laboratory').ids.lab_address.text ,
                "phone_lab":self.parent.get_screen('laboratory').ids.phone_lab.text ,
                "analysis_name":self.parent.get_screen('laboratory').ids.analysis_name.text ,
                "price":float(self.parent.get_screen('laboratory').ids.lab_price.text),
                #"photo":self.parent.get_screen('laboratory').ids.img.source, 
                "paypal_email":self.parent.get_screen('laboratory').ids.lab_payment.text
            }
            user_data = firestoree.collection('users').document(email).get().to_dict()
             
            # التحقق من وجود بيانات للمستخدم
            if user_data:
            # إنشاء قائمة للمنتجات إذا لم تكن موجودة بالفعل
                if 'products' not in user_data:
                    user_data['products'] = [data]
                    firestoree.collection('users').document(email).collection('products').set(user_data)
                else:
                # إضافة بيانات المنتج الجديد إلى قائمة المنتجات
                    user_data['products'].append(data)
                    firestoree.collection('users').document(email).set(user_data)
            else:
                firestoree.collection('users').document(email).collection('products').add(data)
           
             
             
            
            speaker =win.Dispatch("SAPI.SPvoice")
            speaker.Rate = -1
            speaker.Speak("Analysis added successfully")
            
            self.parent.get_screen('laboratory').ids.lab_name.text=""
            self.parent.get_screen('laboratory').ids.lab_address.text=""
            self.parent.get_screen('laboratory').ids.phone_lab.text=""
            self.parent.get_screen('laboratory').ids.analysis_name.text=""
            self.parent.get_screen('laboratory').ids.lab_price.text=""
            #self.parent.get_screen('laboratory').ids.img.source=""
            #self.parent.current="profile"

        except Exception as Error:
             
           
            speaker =win.Dispatch("SAPI.SPvoice")
            speaker.Speak("Analysis not added please check data ")
            
            self.show_error_dialog("Please check data")
             
    
            
    def show_error_dialog(self, error_message):
        dialog = MDDialog(
            title="ُERROR",
            text=error_message,
            size_hint=(0.7, 0.3)
        )
        dialog.open()   
    
class StartScreen(Screen):
    pass

class Login_user(Screen):
    pass
        

class Signup_user(Screen):
    
    def signup_user(self, email, password):
        try:
            auth.create_user_with_email_and_password(email, password)
            data1 = {
                'email': self.ids.email_field.text,
                'password': self.ids.password_field.text,
                'date': self.ids.date_user.text,
                'phone': self.ids.phone.text,
                'user_name': self.ids.user_name.text,
            }
            firestoree.collection("user_email").document(email).set(data1)
            speaker = win.Dispatch("SAPI.SPvoice")
            speaker.Rate = -1
            speaker.Speak("The data has been stored successfully")
            if 'show_lab' in self.manager.screen_names:
                self.manager.current = "show_lab"
        except Exception as Er:
            self.show_error_dialog("The Email is invalid")
             

    def show_error_dialog(self, error_message):
        dialog = MDDialog(
            title="ُERROR",
            text=error_message,
            size_hint=(0.7, 0.3)
        )
        dialog.open() 
         
    
    def show_date_picker(self, instance, value):
        if value:
            date_dialog = MDDatePicker(size_hint=(None, None), size=(300, 400))
            date_dialog.bind(on_save=self.get_date)
            date_dialog.open()

    def get_date(self, instance, value, date_range):
        # حفظ التاريخ المحدد في متغير
        selected_date = value.strftime("%d/%m/%Y")
        # عرض التاريخ في الـ `MDTextField`
        self.ids.date_user.text = selected_date
            

class Choose_entery(Screen):
    pass

class Login_admin(Screen):
    def login_admin(self, email, password):
        
        try:
            # تسجيل الدخول باستخدام Firebase Authentication
            auth.sign_in_with_email_and_password(email.strip(), password)
            
            # تخزين البريد الإلكتروني لاستخدامه لاحقًا في الصفحة Update
            self.email = email
            
            # عند نجاح عملية تسجيل الدخول، تحميل بيانات المستخدم
            user_data = firestoree.collection('users').document(email).collection('products').get()
            for doc in user_data:
                x=doc.to_dict()  
                lab_name=x.get("lab_name","")
                
                if user_data is None:
                    user_data = {"email": email , "lab_name":lab_name}
                    
                
                
                # التحقق من وجود الشاشة "laboratory" قبل التبديل إليها
                if 'laboratory' in self.manager.screen_names:
                    self.parent.get_screen('laboratory').ids.lab_name.text=lab_name
                    # تعيين بيانات المستخدم في الشاشة "laboratory"
                    self.manager.get_screen('laboratory').set_user_data(user_data)
                     
                     
                    # التبديل إلى الشاشة "laboratory"
                    self.manager.current = "profile"
                else:
                    self.show_error_dialog("please check screen")
        except  requests.exceptions.HTTPError as e:
            
            self.show_error_dialog("password or email is error")
            
    def show_error_dialog(self, error_message):
        dialog = MDDialog(
            title="ُERROR",
            text=error_message,
            size_hint=(0.7, 0.3)
        )
        dialog.open() 
    

class Signup_admin(Screen):
    
    def sign_up_admin(self,email, password ):
        try:
            auth.create_user_with_email_and_password(email.strip(), password)  # إنشاء المستخدم في Firebase Authentication
            
            # التحقق من أن البيانات غير فارغة
            if not self.ids.laboratory_name.text or not self.ids.password_admin.text or not self.ids.email_admin.text or not self.ids.address_admin.text or not self.ids.phone_admin.text:
                self.show_error_dialog("Please Enter Data")
                return  # عودة من الدالة إذا كانت البيانات غير كافية
            
            analysis_id = str(uuid.uuid4())  # إنشاء معرف عشوائي للمعمل
            data = {
                "lab_name": self.ids.laboratory_name.text,
                "lab_address": self.ids.address_admin.text,
                "phone_lab": self.ids.phone_admin.text,
                "email": self.ids.email_admin.text,
                "password": self.ids.password_admin.text,
            }
             
            speaker =win.Dispatch("SAPI.SPvoice")
            speaker.Speak("The data has been stored successfully")
            # التحقق من وجود الشاشة "laboratory" قبل التبديل إليها
            if 'laboratory' in self.manager.screen_names:
                # التبديل إلى الشاشة "laboratory"
                
                # تعيين بيانات المستخدم في الشاشة "laboratory"
                self.manager.get_screen('laboratory').set_user_data(data)
                self.manager.current = "laboratory"
                
                
            else:
                 
            
            # حفظ البيانات في قاعدة البيانات Firestore باستخدام المعرف العشوائي
                firestoree.collection("Admin_Email").document(email).set(data)
            
             
            
            
            
            #self.parent.current = "main"
        except Exception as E:
            self.show_error_dialog("The Email is not valid")
             

    def show_error_dialog(self, error_message):
        dialog = MDDialog(
            title="ERROR",
            text=error_message,
            size_hint=(0.7, 0.3)
        )
        dialog.open()
class Choose_signup(Screen):
    pass

class Profile(Screen):
    def on_pre_enter(self):
        # التحقق من أن حقل البحث ليس فارغًا قبل تنفيذ return_data()
        if self.parent.get_screen('login_admin').ids.email_field.text.strip():
            self.return_data()
        if self.parent.get_screen('signup_admin').ids.email_admin.text.strip():
            self.return_data_signup()
            
        
            
    def return_data(self):
        return_analysis = self.parent.get_screen('login_admin').ids.email_field.text.strip()  # الحصول على النص المدخل في حقل البحث وحذف الفراغات الزائدة
        # تحديث عرض الصفحة فقط إذا كان هناك نص مدخل في حقل البحث
        if return_analysis:
            docs = firestoree.collection("users").document(return_analysis).collection("products").where("email", "==", return_analysis).get()
            retreive_data = self.ids.retreive_data
            retreive_data.clear_widgets()  # تفريغ العناصر القديمة

            for doc in docs:
                data = doc.to_dict()
                lab_name=data.get("lab_name","")
                lab_address=data.get("lab_address","")
                phone_lab=data.get("phone_lab","")
                analysis_name = data.get("analysis_name", "")
                lab_price = str(data.get("price", ""))
                photo = data.get("photo", "")

                card_layout = GridLayout( padding=10, spacing=10,cols=2)
            
                # Agregar los elementos al BoxLayout
   
                card_layout.add_widget(MDLabel(text=f"Lab : {lab_name}",theme_text_color="Custom",text_color="red" ,font_style="Button"))
                #card_layout.add_widget(Image(source=photo))
                card_layout.add_widget(MDLabel(text=f"Phone: {phone_lab}",theme_text_color="Custom",text_color="green" ,font_style="Button"))

                card_layout.add_widget(MDLabel(text=f"Analysis Name: {analysis_name}",theme_text_color="Custom",text_color="red" ,font_style="Button"))
                card_layout.add_widget(MDLabel(text=f"Price: {lab_price}",theme_text_color="Custom",text_color="green" ,font_style="Button"))            
                card_layout.add_widget(MDLabel(text=f"Address: {lab_address}",theme_text_color="Custom",text_color="blue" ,font_style="Body1"))
                # Crear el MDCard
                card = MDCard(size_hint_y=None, height=dp(200), padding=dp(10), md_bg_color="gold",radius= [40,])
                
                # Agregar el BoxLayout al MDCard
                card.add_widget(card_layout)
                
                # Agregar el MDCard al GridLayout
                retreive_data.add_widget(card)
                
                #self.ids.retreive.text=""
        else:
            self.show_error_dialog("please Enter the Email")
    
    def return_data_signup(self):
        return_analysis_signup = self.parent.get_screen('signup_admin').ids.email_admin.text.strip()  # الحصول على النص المدخل في حقل البحث وحذف الفراغات الزائدة
        # تحديث عرض الصفحة فقط إذا كان هناك نص مدخل في حقل البحث
        if return_analysis_signup:
            docs = firestoree.collection("users").document(return_analysis_signup).collection("products").where("email", "==", return_analysis_signup).get()
            retreive_data = self.ids.retreive_data
            retreive_data.clear_widgets()  # تفريغ العناصر القديمة

            for doc in docs:
                data = doc.to_dict()
                lab_name=data.get("lab_name","")
                lab_address=data.get("lab_address","")
                phone_lab=data.get("phone_lab","")
                analysis_name = data.get("analysis_name", "")
                lab_price = str(data.get("price", ""))
                photo = data.get("photo", "")

                card_layout = GridLayout( padding=10, spacing=10,cols=2)
            
                # Agregar los elementos al BoxLayout
   
                card_layout.add_widget(MDLabel(text=f"Lab : {lab_name}",theme_text_color="Custom",text_color="red" ,font_style="Button"))
                #card_layout.add_widget(Image(source=photo))
                card_layout.add_widget(MDLabel(text=f"Phone: {phone_lab}",theme_text_color="Custom",text_color="green" ,font_style="Button"))

                card_layout.add_widget(MDLabel(text=f"Analysis Name: {analysis_name}",theme_text_color="Custom",text_color="red" ,font_style="Button"))
                card_layout.add_widget(MDLabel(text=f"Price: {lab_price}",theme_text_color="Custom",text_color="green" ,font_style="Button"))            
                card_layout.add_widget(MDLabel(text=f"Address: {lab_address}",theme_text_color="Custom",text_color="blue" ,font_style="Body1"))
                # Crear el MDCard
                card = MDCard(size_hint_y=None, height=dp(200), padding=dp(10), md_bg_color="gold",radius= [40,])
                
                # Agregar el BoxLayout al MDCard
                card.add_widget(card_layout)
                
                # Agregar el MDCard al GridLayout
                retreive_data.add_widget(card)
                
                #self.ids.retreive.text=""
        else:
            self.show_error_dialog("please Enter the Email")

    def show_error_dialog(self, error_message):
        dialog = MDDialog(
            title="ERROR",
            text=error_message,
            size_hint=(0.7, 0.3)
        )
        dialog.open()

           
class Show_lab(Screen):
    

        
    def on_pre_enter(self):
        # حذف المنتجات المعروضة حاليًا قبل عرض منتجات المعمل الجديدة
        self.ids.products_grid.clear_widgets()
        # عرض قائمة المعامل
        self.display_lab_info()

    def show_data(self, lab_name):
        products_grid = self.ids.products_grid
        admin_docs = firestoree.collection("Admin_Email").get()
        for doc in admin_docs:
            admin_data = doc.to_dict()
            email = admin_data.get("email")
            lab_name=admin_data.get("lab_name","")

            card_layout = GridLayout(padding=10, spacing=10, cols=2)
            card_layout.add_widget(MDLabel(text=f"Lab Name: {lab_name}"))
         
            card = MDCard(size_hint_y=None, height=dp(200), padding=dp(10), md_bg_color="pink", radius=[40, ])
            card.add_widget(card_layout)
            products_grid.add_widget(card)

    def show_lab_info(self, lab_name):
        # استدعاء show_data عند النقر على اسم المعمل لعرض منتجات المعمل
        self.show_data(lab_name)
        
    
    def display_lab_info(self):
        products_grid = self.ids.products_grid
        self.ids.products_grid.clear_widgets()
        # عرض أسماء المعامل فقط
        admin_docs = firestoree.collection("Admin_Email").get()
        for doc in admin_docs:
            admin_data = doc.to_dict()
            email = admin_data.get("email")
            lab_name = admin_data.get("lab_name")
            lab_address = admin_data.get("lab_address")
            
            card_layout = GridLayout(padding=5, spacing=5, cols=1,)
            card_layout.add_widget(MDLabel(text=f"Lab Name: {lab_name}",
            theme_text_color="Custom",text_color="red",font_style="Button"
            ))
            card_layout.add_widget(MDLabel(text=f"Lab Address: {lab_address}",theme_text_color="Custom",text_color="red" , font_style="Button"))
            
            
            lab_button = MDRaisedButton(text=f"Go to : {lab_name}",md_bg_color="green", on_release=lambda btn, lab_name=lab_name: self.show_lab_info(lab_name))
            lab_button.bind(on_release=lambda btn, lab_name=lab_name: self.go_to_analysis_screen(lab_name))  # تمرير lab_name
            card_layout.add_widget(lab_button)
            
            card = MDCard(size_hint_y=None, height=dp(200), padding=dp(10), md_bg_color="gold", radius=[40, ])
            card.add_widget(card_layout)
            products_grid.add_widget(card)
        
    def go_to_analysis_screen(self, lab_name):
        
        self.manager.get_screen('show_analysis').show_data(lab_name)
        self.manager.current = 'show_analysis'  # تحديد الشاشة التي تريد الانتقال إليها

    def search_product(self):
        
        show_analysis_screen = self.manager.get_screen('show_analysis')
        search_text = self.ids.search_field.text.strip()  # الحصول على النص المدخل في حقل البحث وحذف الفراغات الزائدة

        # تحديث عرض الصفحة فقط إذا كان هناك نص مدخل في حقل البحث
        if search_text:
            products_grid = self.ids.products_grid
            products_grid.clear_widgets()  # تفريغ العناصر القديمة

            # جلب جميع الوثائق التي تطابق البحث
            admin_docs = firestoree.collection("Admin_Email").get()
            for doc in admin_docs:
                admin_data = doc.to_dict()
                lab_address = admin_data.get("lab_address", "")
                
                
                email = admin_data.get("email")
                docs = firestoree.collection("users").document(email).collection("products").get()
                for doc in docs:
                    data = doc.to_dict()
                    phone_lab = data.get("phone_lab", "")
                    analysis_name = data.get("analysis_name", "")
                    lab_price = str(data.get("price", ""))
                    lab_address = data.get("lab_address", "")
                    lab_name = data.get("lab_name", "")
                    payment=data.get("paypal_email","")
                
                    # التحقق مما إذا كان عنوان المعمل يحتوي على النص المطلوب
                    if search_text in lab_address:
                        lab_name = admin_data.get("lab_name", "")
                    # phone_lab = admin_data.get("phone_lab", "")

                        card_layout = GridLayout(padding=5, spacing=5, cols=1)
                        card_layout.add_widget(MDLabel(text=f"Lab Name: {lab_name}",theme_text_color="Custom",text_color="red" , font_style="Button"))
                        card_layout.add_widget(MDLabel(text=f"Lab Address: {lab_address}" ,theme_text_color="Custom",text_color="blue" , font_style="Button"))
                        
                        lab_button = MDRaisedButton(text=f"Lab Name: {lab_name}",md_bg_color="red" ,on_release=lambda btn, lab_name=lab_name: self.show_lab_info(lab_name))
                        lab_button.bind(on_release=lambda btn, lab_name=lab_name: self.go_to_analysis_screen(lab_name))  # تمرير lab_name
                        card_layout.add_widget(lab_button)
                        
                        card = MDCard(size_hint_y=None, height=dp(200), padding=dp(10), md_bg_color="gold", radius=[40, ])
                        card.add_widget(card_layout)
                        products_grid.add_widget(card)
                        self.ids.search_field.text = ""
                        
                    elif search_text in analysis_name:
                        
                        card_layout = GridLayout(padding=10, spacing=10, cols=2)
                        #card_layout.add_widget(MDLabel(text=f"Lab Name: {lab_name}"))
                        card_layout.add_widget(MDLabel(text=f"Name: {analysis_name}",theme_text_color="Custom",text_color="red" ,font_style="Button"))
                        card_layout.add_widget(MDLabel(text=f"Address: {lab_address}",theme_text_color="Custom",text_color="green" ,font_style="Button"))
                        card_layout.add_widget(MDLabel(text=f"Price: {lab_price}",theme_text_color="Custom",text_color="red" ,font_style="Button"))
                        card_layout.add_widget(MDLabel(text=f"lab_name: {lab_name}",theme_text_color="Custom",text_color="green" ,font_style="Button"))
                        
                        whatsapp_button = MDIconButton(icon="whatsapp", font_size=20, md_bg_color="teal")
                        whatsapp_button.bind(on_release=lambda button, phone_number=phone_lab: show_analysis_screen.contact_whatsapp(phone_number))
                        card_layout.add_widget(whatsapp_button)

                        phone_button = MDIconButton(icon="phone", font_size=20, md_bg_color="teal")
                        phone_button.bind(on_release=lambda button, phone_number=phone_lab: show_analysis_screen.call_number(phone_number))
                        card_layout.add_widget(phone_button)
                        
                        # إضافة زر للإبلاغ
                        report_button = MDIconButton(icon="alert-circle", size_hint_y=None, height=50 ,md_bg_color="red")
                        report_button.bind(on_release=lambda instance, name=analysis_name: show_analysis_screen.send_email_popup(name))
                        card_layout.add_widget(report_button)
                        
                        pay_button = MDRaisedButton(text="pay", size_hint_y=None, height=50)
                        pay_button.bind(on_release=lambda instance, price=lab_price , mail=payment : show_analysis_screen.create_paypal_payment(mail, price))
                        card_layout.add_widget(pay_button)

                        card = MDCard(size_hint_y=None, height=dp(200), padding=dp(10), md_bg_color="gold", radius=[40, ])
                        card.add_widget(card_layout)
                        products_grid.add_widget(card)
                        
                    
class RootScreen(ScreenManager):
    pass


Builder.load_file("main.kv")
class Slope(MDApp): 
    
    def build(self):
        self.title="Online Lab" 
        
        
        
        speaker =win.Dispatch("SAPI.SPvoice")
        speaker.Rate = -1
        speaker.Speak("Welcome to the application. ")
        
        return RootScreen()
    
    def login(self, email, password):
        try:
            # تسجيل الدخول باستخدام Firebase Authentication
            auth.sign_in_with_email_and_password(email.strip(), password)
            user_docs = firestoree.collection("user_email").document(email).get()
            
            user_data = user_docs.to_dict()
            name = user_data.get("user_name","")
            
            speaker =win.Dispatch("SAPI.SPvoice")
            speaker.Rate = -2
            speaker.Speak(f"Welcome {name}")
            
            # يمكنك إضافة مزيد من الكود هنا، مثل تحويل المستخدم إلى الشاشة المطلوبة
            self.root.current="show_lab"
        except requests.exceptions.HTTPError as e:
            # إذا كان هناك خطأ أثناء تسجيل الدخول، يمكنك عرض رسالة الخطأ
           
            self.show_error_dialog("password or email is error")
    def show_error_dialog(self, error_message):
        dialog = MDDialog(
            title="ُERROR",
            text=error_message,
            size_hint=(0.7, 0.3)
        )
        dialog.open() 
    
    
    
    
        



        
if __name__ == "__main__":
    LabelBase.register(name="MPoppins" , fn_regular="Poppins-Medium.ttf")
    LabelBase.register(name="BPoppins" , fn_regular="Poppins-SemiBold.ttf")

    Slope().run()
