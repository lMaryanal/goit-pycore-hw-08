import datetime
from datetime import datetime, timedelta
from collections import UserDict
import re
import pickle



class ValueFieldError(Exception):
    pass

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
     pass

class Phone(Field):
    def __init__(self, value):
        if not re.search("\d{10}", value) or len(value) > 10:
            raise ValueFieldError("Please enter a 10-digit number.")
        super().__init__(value)
    
    def __eq__(self, other):
        if type(other) == Phone:
            return self.value == other
        if type(other) == str:
            return str(self.value) == other
        if not isinstance(other, Phone):
            return NotImplemented
    def __raeq__(self, other):
        if type(other) == Phone:
            return self.value == other
        if type(other) == str:
            return str(self.value) == other
        if not isinstance(other, Phone):
            return NotImplemented
        

class Birthday(Field):
    def __init__(self, value):
        try:
            datetime_object = (datetime.strptime(value, "%d.%m.%Y")).date()
            super().__init__(datetime_object)
        except ValueError:
            raise ValueFieldError("Invalid date format. Use DD.MM.YYYY")


class Record:
    def __init__(self, name: str):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone: str):
        self.phones.append(Phone(phone))
            
    
    def remove_phone(self, deleted_phone: str):
        for phone in self.phones:
            if phone == deleted_phone:
                self.phones.remove(phone)

    def edit_phone(self, old_number: str, new_number: str):
        for phone in self.phones:
            if phone == old_number:
                self.phones[self.phones.index(phone)] = Phone(new_number)
                return()
        raise KeyError

    def find_phone(self, desired_phone: str):
        for phone in self.phones:
            if desired_phone == phone :
                return(phone)

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)


    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"

class AddressBook(UserDict):

    def add_record(self, record: Record):
        self.data[record.name] = record

    def find(self, search_name: str):
        for name in self.data:
            if search_name == str(name):
                return(self.data.get(name))
            
    def delete(self, search_name: str):
        for name in self.data:
            if search_name == str(name):
                del self.data[name]
                break
    
    def get_upcoming_birthdays(self): #повертає словник зіменами та датами привітання людей з днем народження на 7 днів вперед
        today = datetime.today().date()
        coming_birthdays = []
        for user in self.data:
            if not (self.data.get(user)).birthday:
                continue
            user_birthday = ((self.data.get(user)).birthday.value)

            #змінює рік народження на сьогоднішній
            birthday_this_year = datetime(today.year, user_birthday.month, user_birthday.day).date()

            #якщо др пройшов, додае до року 1
            if birthday_this_year < today:
                birthday_this_year = datetime(birthday_this_year.year+1, birthday_this_year.month, birthday_this_year.day).date()
                
            
            days_before_birthday = (birthday_this_year - today).days

            if days_before_birthday <= 7:
                if birthday_this_year.weekday() >=5: #якщо др припав на вихідній, переносить привітання на наступний понеділок
                    days_before_monday = 7 - birthday_this_year.weekday()
                    greetings_day = birthday_this_year + timedelta(days=days_before_monday)
                else:
                    greetings_day = birthday_this_year
                coming_birthdays.append({"name":user.value, "birthday greetings": greetings_day.strftime("%d.%m.%Y")})
        return(coming_birthdays)

def input_error(func):
      #function_name = str(func).split(" ")[1].split(".")[1]
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueFieldError as e:
            return e
        except ValueError:
            return "Give me name and phone please."
        except KeyError:
            return "information does not exist."
        except IndexError:
            return "Give me name please."
        except AttributeError:
            return "no contact exists"

    return inner

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return (cmd, *args)

@input_error
def add_contact(args, book):
    name, phone = args
    if book.find(name):
        contact =  book.find(name)
        contact.add_phone(phone)
    else:
        contact = Record(name)
        contact.add_phone(phone)
        book.add_record(contact)
    return "Contact added."

@input_error
def change_contact(args, book):
    if len(args) != 3:
        return("Give me name, old phone and new phone please.")
    name, old_phone, new_phone = args
    contact = book.find(name)
    contact.edit_phone(old_phone, new_phone)
    return "Contact updated."

@input_error
def show_phone(args, book):
    name = args[0]
    if not book.find(name):
        return "no contact exists"
    return (book.find(name))
    
# @input_error
# def show_all(book):
#     all = []
#     for name, record in book.data.items():
#         all.append(str(record))
#     return (all)

@input_error
def add_birthday(args, book):
    if len(args) != 2:
        return("Give me name and date please.")
    name, date = args
    contact = book.find(name)
    contact.add_birthday(date)
    return("Birthday added.")


@input_error
def show_birthday(args, book):
    name = args[0]
    contact = book.find(name)
    if not contact.birthday:
        return("Birthday date not added.")
    date = contact.birthday.value
    return(date.strftime("%d.%m.%Y"))


@input_error
def birthdays(book):
   return(book.get_upcoming_birthdays())

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено

def main():
    book = load_data()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))
        
        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            if not book:
                print ("contact list is empty.")
            for name, record in book.data.items():
                print(record)

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            this_week = birthdays(book)
            if this_week:
                print("Birthdays this week.")
                for this_week in birthdays(book):
                    print(this_week)
            else:
                print("There are no birthdays this week.")

        else:
            print("Invalid command.")
    save_data(book)




if __name__=="__main__":
    main()