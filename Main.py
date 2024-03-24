from tkinter import font,messagebox,ttk
import mysql.connector,random,tkinter,random,re,os
from tkinter import *
from dotenv import load_dotenv


###ENV USING
load_dotenv()

mydb = mysql.connector.connect(
    host = os.getenv('HOST'),
    user = os.getenv('USER'),
    password = os.getenv('PASSWORD'),
    database = os.getenv("SCHEMA")
)

background_path = os.getenv("BACKGROUNDPATH")
table_name = os.getenv("TABLE")
cur = mydb.cursor(buffered=True)

#CONST
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
is_available_add_window = True
is_available_delete_window = True


from_database_array = []
helper_holding_data_array = []
current_word = []
listbox_arr = []
#Function to load data from DataBase
def loadingDB():
    cur.execute(f'SELECT * FROM {table_name}')
    for i in cur:
        i = list(i)
        if i not in from_database_array:
            from_database_array.append(i)
            helper_holding_data_array.append(i)
            listbox_arr.append(i[0:3])





#Main Buttons and Functionality
"""
implementation of the main buttons:
word_drawing() -> random word selection
show_polish_word() -> funcionality responsible for displaying a word in Polish
view() -> view how a word presented in Polish sounds in English
know() -> indicating that the word is known to us
notknow() -> indicating that the word is not known to us and will be available again
new_series() -> refreshes the application and allows you to load a new series

Translated with DeepL.com (free version)
"""

#Generating random record
def word_drawing():
    if helper_holding_data_array:
        random_record = random.choice(helper_holding_data_array)
        current_word.append(random_record)
        return random_record

#Function to display polish word
#Text of polish_word is created in function, later used in Label
def show_polish_word():
    if not helper_holding_data_array:
        set_to_zero()
        messagebox.showinfo(title="Info", message="Znasz już wszystkie słowa")
        #Set text to " " when all the words are known and we don't have anything to show.
        polish_text = Text(window, background="#2b2b2b", font=('Consolas', 15, 'bold'), wrap=WORD, height=14, width=16, fg="white")
        polish_text.insert(END, " ")
        polish_text.config(relief="flat")
        polish_text.place(x=100, y=120)
        return
    #drawing random word from all possible options from database
    random_record = word_drawing()
    try:
        #Set text to random word
        polish_word  = random_record[1]
        polish_text = Text(window, background="#2b2b2b", font=('Consolas', 15, 'bold'), wrap=WORD, height=14, width=16, fg="white")
        polish_text.insert(END, polish_word)
        polish_text.tag_configure("center", justify="center")
        polish_text.tag_add("center", "1.0", "end")
        num_lines = polish_text.get("1.0", "end").count("\n")
        padding_top = int((14 - num_lines) / 2)
        padding_bottom = 14 - num_lines - padding_top
        polish_text.insert("1.0", "\n" * padding_top)
        polish_text.insert(END, "\n" * padding_bottom)
        polish_text.config(relief="flat")
        polish_text.config(state="disabled")
        polish_text.place(x=100, y=120)
    except Exception as e:
        print("Error",e)



#Functionality of "Pokaż" button
#Shows a word in English that was previously hidden
def view():
    if not helper_holding_data_array:
        return
    try:
        #Set text to random word
        english_word = current_word[0][2]
        english_text = Text(window, background="#2b2b2b", font=('Consolas', 15, 'bold'), wrap=WORD, height=14, width=16, fg="white")
        english_text.insert(END, english_word)
        english_text.tag_configure("center", justify="center")
        num_lines = english_text.get("1.0", "end").count("\n")
        padding_top = int((14 - num_lines) / 2)
        padding_bottom = 14 - num_lines - padding_top
        english_text.insert("1.0", "\n" * padding_top)
        english_text.insert(END, "\n" * padding_bottom)
        english_text.tag_add("center", "1.0", "end")
        english_text.configure(state="disabled")
        english_text.config(relief="flat")
        english_text.place(x=520, y=120)
        window.update()
    except Exception as e:
        print("Error",e)

#Functionality of "Wiem" button
def know():
    if not helper_holding_data_array:
        return
    
    try:
        #If know() function is prompted, update know field in database to 1 and current word wont't be repeated until new series
        random_record = current_word[0]
        helper_holding_data_array.remove(random_record)
        random_number = random_record[0]
        current_word.clear()
        cur.execute(f"UPDATE {table_name} SET know=1 WHERE translate_id = {random_number}")
        mydb.commit()
        default_label = Label(window, background="#2b2b2b", font=('Consolas', 15, 'bold'), width=16, height=14,
                            fg="white")
        default_label.place(x=520, y=120)
        show_polish_word()
    except Exception as e:
        print("Error",e)


#Functionality of "Nie wiem" button
def notknow():
    try:
        #When the know() function is called, the know field in the database is updated to 0 and the current word is repeated until the user knows every word.
        random_record = current_word[0]
        random_number = random_record[0]
        current_word.clear()
        cur.execute(f"UPDATE {table_name} SET know=0 WHERE translate_id = {random_number}")
        mydb.commit()
        default_label = Label(window, background="#2b2b2b", font=('Consolas', 15, 'bold'), width=16, height=14,
                            fg="white")
        default_label.place(x=520, y=120)
        show_polish_word()
    except Exception as e:
        print("Error",e)


#If the user has completed the entire series, a new series can be started using this function
def new_series():
    global window
    from_database_array.clear()
    helper_holding_data_array.clear()
    current_word.clear()
    listbox_arr.clear()
    window.destroy()
    create_window()










#set_to_zero() is used in various parts of the code to set the word state as unknown for each
#After closing app we set all words as unknow
def set_to_zero():
    cur.execute(f"UPDATE {table_name} SET know=0")
    mydb.commit()


#Below are the functions for the menubar buttons 'add word', 'delete word','show words'
"""
add_word_button() odpowiada za stworzenie pola w którym dodajemy wyrazy
add_word() pokrywa funkcjonalność dodania wyrazu do bazy dancyh i odświeżenia statusu

 
delete_word_button() odpowiada za stworzenie listboxa w którym możemy usunąć wyrazy
delete() pokrywa funkcjonalność usunięcia wyrazu do bazy dancyh i odświeżenia statusu

 
show_words_button() pozwala na sprawdzenie aktualnych słów w bazie danych
"""



def add_word_button():
    is_available_add_window = True

    def on_closing():
        loadingDB()
        add_window.destroy()
    
    if is_available_add_window:

        #Creating Notebook to place at the top menu bar,creating new window where we can add word, setting width,height,x,y and some additional configuration
        notebook = ttk.Notebook(window)
        add_window = Frame(notebook)
        notebook.add(add_window, text="Dodaj słowo")
        is_available_add_window = False
        add_window = Tk()
        add_window.resizable(False, False)
        add_window.title('Dodaj słowo')
        x = window.winfo_x()
        y = window.winfo_y()
        add_window.geometry(f"{WINDOW_WIDTH//2}x{WINDOW_HEIGHT//2}+{(x+WINDOW_WIDTH//4)}+{(y+WINDOW_HEIGHT//4)}")
        add_window.configure(bg="lightblue")
        add_window.grid_columnconfigure(0, weight=1)
        add_window.grid_columnconfigure(1, weight=1)


        #Set custom font
        custom_font = font.Font(family="Helvetica", size=12, weight="bold", slant="italic")

        #Empty label to better placing other components
        empty = Label(add_window, text="", bg="lightblue", fg="black", font=custom_font)
        empty.grid(row=0, column=0, padx=0, pady=55)


        #Label and input form for polish word
        polish_word_label = Label(add_window, text="Polskie słowo: ", bg="lightblue", fg="black", font=custom_font)
        polish_word_label.grid(row=0, column=0, padx=5, pady=0)
        polish_word_entry = Entry(add_window, font=custom_font)
        polish_word_entry.grid(row=0, column=1, padx=5, pady=0)

        #Label and input form for english word
        english_word_label = Label(add_window, text="Angielskie słowo: ", bg="lightblue", fg="black", font=custom_font)
        english_word_label.grid(row=1, column=0, padx=5, pady=0)
        english_word_entry = Entry(add_window, font=custom_font)
        english_word_entry.grid(row=1, column=1, padx=5, pady=0)

        #Button to add word
        polish_word_button = Button(add_window, text="Dodaj słowo", command=lambda: add_word(polish_word_entry, english_word_entry,add_window), bg="lightgreen", fg="black", font=custom_font)
        polish_word_button.grid(row=2, column=1, padx=5, pady=15)
        add_window.protocol("WM_DELETE_WINDOW", on_closing)

#Function using to add word after clicking on 'dodaj słowo' button
def add_word(polish_word_entry,english_word_entry,add_window):

    #Getting words from entry
    
    polish_word_value = polish_word_entry.get()
    english_word_value = english_word_entry.get()

    word_pattern = r'^[a-zA-ZżźćńółęąśŻŹĆĄŚĘŁÓŃ\s]+$'

    #Checking if the words entered are correct
    if re.match(word_pattern,polish_word_value) and re.match(word_pattern,english_word_value):
        #Deleting after use off add button to clear input field
        polish_word_entry.delete(0,END)
        english_word_entry.delete(0,END)

        #Making changes in DataBase
        cur.execute(f"INSERT INTO {table_name}(polish_word,english_word,know) VALUES ('{polish_word_value}','{english_word_value}',0)")
        mydb.commit()
        loadingDB()
    else:
        messagebox.showerror(title="Error", message="Wprowadzone słowo musi zawierać tylko litery")
        add_window.destroy()



#Functionality of 'usun słowo' button
def delete_word_button():
    is_available_delete_window = True

    def on_closing():
        delete_window.destroy()
    
    if is_available_delete_window:
        delete_window = Tk()
        delete_window.resizable(False, False)
        delete_window.title('Usuń słowo')
        is_available_delete_window = False
        x = window.winfo_x()
        y = window.winfo_y()
        delete_window.geometry(f"{WINDOW_WIDTH//2}x{WINDOW_HEIGHT//2}+{(x+WINDOW_WIDTH//4)}+{(y+WINDOW_HEIGHT//4)}")
        delete_window.configure(bg="lightblue")
        #Creating Notebook to place at the top menu bar,creating new window where we can delete word, setting width,height,x,y and some additional configuration
        delete_window_frame = Frame(delete_window)
        scrollbar= ttk.Scrollbar(delete_window_frame, orient= 'vertical')


        #Better placing of delete_window_frame
        delete_window_frame.grid_columnconfigure(0, weight=1)
        delete_window_frame.grid_columnconfigure(1, weight=1)
        #Setting custom font

        custom_font = font.Font(family="Helvetica", size=12, weight="bold")

        #Making listbox where we store data 
        listbox = Listbox(delete_window_frame,width=50,font=custom_font,selectbackground="#E94242",yscrollcommand=scrollbar.set,selectmode=SINGLE,activestyle=tkinter.NONE)
        scrollbar.config(command=listbox.yview)
        listbox.config(justify=tkinter.CENTER)
        scrollbar.pack(side= RIGHT, fill= Y)
        delete_window_frame.pack()
        listbox.pack()
        #Placing data from db in listbox
        for item in listbox_arr:
            #Setting the correct formatting of the text
            l1 = len(item[1])
            l2 = len(item[2])
            o1 = 30-l1
            o2 = 30-l2
            o3=50
            o0 = 15
            #Formatting text to store the id in such a way that it is not visible to the user
            formatted_text = "{:^{o0}} {:^{o1}}  {:^{o2}} {:^{o3}}".format(" ",item[1],item[2],item[0],o0=o0, o1=o1, o2=o2,o3=o3)
            listbox.insert(END, formatted_text)

        #Button to delete word
        listbox_delete_button = Button(delete_window,text="Usuń słowo",command=lambda: delete(listbox,delete_window))
        listbox_delete_button.pack(pady=10)
        
        delete_window.protocol("WM_DELETE_WINDOW", on_closing)


#Delete function to delete word when clicking on 'usuń słowo' in the menubar
def delete(listbox,delete_window):

    selected_index = listbox.curselection()
    
    if selected_index:
        selected_item = listbox.get(selected_index[0]) 
        #Here is a feature that allows you to isolate individual words in an appropriate way
        selected_item = selected_item.lstrip()
        selected_item = selected_item.rstrip()
        length_of_first = 0
        i=0
        while selected_item:
            if selected_item[i] == ' ' and selected_item[i+1] == ' ':
                length_of_first = i
                break
            i+=1
        listbox.delete(selected_index)
        parts = selected_item.split()
        id = parts[-1]
        polish_word = selected_item[:length_of_first]
        
        english_word = selected_item[length_of_first:-len(str(id))].strip()
        #Usuwanie rekordu z bazy danych
    try:
        listbox_arr.remove([int(id), polish_word, english_word])
    except:
        messagebox.showerror(title="Error", message="Zaznacz słowo")
        delete_window.destroy()

    cur.execute(f"DELETE FROM {table_name} WHERE translate_id={id}")
    mydb.commit()


def show_words_button():
    is_available_delete_window = True

    def on_closing():
        show_window.destroy()
    
    if is_available_delete_window:

        #Creating Notebook to place at the top menu bar,creating new window where we can delete word, setting width,height,x,y and some additional configuration
        show_window = Tk()
        show_window.resizable(False, False)
        show_window.title('Pokaż słowa')
        is_available_delete_window = False
        x = window.winfo_x()
        y = window.winfo_y()
        show_window.geometry(f"{WINDOW_WIDTH//2}x{WINDOW_HEIGHT//2}+{(x+WINDOW_WIDTH//4)}+{(y+WINDOW_HEIGHT//4)}")
        show_window.configure(bg="lightblue")


        show_window_frame = Frame(show_window)
        scrollbar= ttk.Scrollbar(show_window_frame, orient= 'vertical')

        show_window_frame.grid_columnconfigure(0, weight=1)
        show_window_frame.grid_columnconfigure(1, weight=1)

        custom_font = font.Font(family="Helvetica", size=12, weight="bold")


        #Making listbox where we store data 
        listbox = Listbox(show_window_frame,width=50,height=15,font=custom_font,selectbackground="#E94242",yscrollcommand=scrollbar.set,selectmode=SINGLE,activestyle=tkinter.NONE)
        scrollbar.config(command=listbox.yview)
        listbox.config(justify=tkinter.CENTER)
        scrollbar.pack(side= RIGHT, fill= Y)
        show_window_frame.pack()
        listbox.pack(pady=5)
        
        #Placing data from db in listbox
        for item in listbox_arr:
            l1 = len(item[1])
            l2 = len(item[2])
            o1 = 30-l1
            o2 = 30-l2
            o3=50
            o0 = 15
            #formatting text to store the id in such a way that it is not visible to the user
            formatted_text = "{:^{o0}} {:^{o1}}  {:^{o2}} {:^{o3}}".format(" ",item[1],item[2],item[0],o0=o0, o1=o1, o2=o2,o3=o3)
            listbox.insert(END, formatted_text)
        show_window.protocol("WM_DELETE_WINDOW", on_closing)


#Main GUI
def create_window():
    global window
    window = Tk()
    window.resizable(False, False)
    window.grab_set()
    menubar = Menu(window)
    window.config(menu=menubar)

    #Adding components to menubar
    menubar.add_cascade(label="Dodaj słowo", command=add_word_button)
    menubar.add_cascade(label="Usuń słowo",command=delete_word_button)
    menubar.add_cascade(label="Pokaż słowa", command=show_words_button)

    #Setting the correct window size
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = int((screen_width / 2) - (WINDOW_WIDTH / 2))
    y = int((screen_height / 2) - (WINDOW_HEIGHT / 2))
    window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")
    window.title("TranslateAPP")
    window.resizable(False, False)

    #Setting background image
    backgroundImage = PhotoImage(file=background_path)
    background_label = Label(window, image=backgroundImage, width=800, height=600)
    background_label.pack()

    #Here is used loadingDB() to synchronize data in program with database and show_polish_word() to load Labels
    loadingDB()
    show_polish_word()

    #Label for english word
    english_label = Label(window, background="#2b2b2b", font=('Consolas', 15, 'bold'), width=16, height=14, fg="white")
    english_label.place(x=520, y=120)

    #Label for viewing english word previously hidden
    view_button = Button(window, text="Pokaż", font=('Consolas', 15, 'bold'), command=view, width=16, height=1)
    view_button.place(x=520, y=460)

    #Button to set word as know
    know_button = Button(window, text="Wiem", font=('Consolas', 15, 'bold'), command=know, width=16, height=1)
    know_button.place(x=100, y=520)

    #Button to set word as notknow
    notknow_button = Button(window, text="Nie wiem", font=('Consolas', 15, 'bold'), command=notknow, width=16, height=1)
    notknow_button.place(x=520, y=520)

    #Button to start new series with updated data
    new_series_button = Button(window, text="Rozpocznij nową serię", font=('Consolas', 10, 'bold'), command=new_series, width=21, height=1)
    new_series_button.place(x=5, y=5)

    window.mainloop()
    set_to_zero()

if __name__ == '__main__':
    create_window()