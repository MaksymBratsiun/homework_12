
from collections import UserDict
from datetime import datetime, timedelta
import pickle


class Field:
    def __init__(self, value):
        self._value = None
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value


class Birthday(Field):
    @Field.value.setter
    def value(self, value):
        if len(value) != 5:
            raise ValueError("Date of birth is incorrect.")
        if int(value[0:2]) > 12:
                raise ValueError("Date of birth is incorrect.")
        if value[0:2] in ("01", "03", "05", "07", "08", "10", "12"):
            if int(value[3:5]) > 31:
                raise ValueError("Date of birth is incorrect.")
        elif value[0:2] in ("04", "06", "09", "11"):
            if int(value[3:5]) > 30:
                raise ValueError("Date of birth is incorrect.")
        elif value[0:2] == "02":
            if int(value[3:5]) > 28:
                raise ValueError("Date of birth is incorrect.")
        self._value = value


class Name(Field):
    @Field.value.setter
    def value(self, value):
        if not value.isalpha():
            raise ValueError
        self._value = value


class Phone(Field):
    @Field.value.setter
    def value(self, value):
        sanitaze_value = ''
        not_num = ("+", "-", "(", ")", "-", "/")
        for char in value:
            if char not in not_num:
                sanitaze_value += char
        if len(sanitaze_value) < 5 or len(sanitaze_value) > 12:
            raise ValueError("Phone must contains 5-12 symbols.")
        if not sanitaze_value.isnumeric():
            raise ValueError('Wrong phones.')
        self._value = sanitaze_value


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        set_phones = set({phone})
        for number in self.phones:
            set_phones.add(number.value)
        self.phones.clear()
        list_phones = list(set_phones)
        for number in list_phones:
            self.phones.append(Phone(number))

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def days_to_birthday(self):
        if self.birthday:
            today = datetime.now()
            birthday = datetime(year=datetime.now().year,
                                month=int(self.birthday.value[0:2]),
                                day=int(self.birthday.value[3:5]))
            if today > birthday:
                birthday = datetime(year=datetime.now().year + 1,
                                    month=int(self.birthday.value[0:2]),
                                    day=int(self.birthday.value[3:5]))
            return f"{(birthday - today + timedelta(days=1)).days} days to {self.name.value.title()}'s birthday"
        else:
            return f"{self.name.value.title()}'s date of birth  not set"

    def get_info(self):
        phones_info = ""
        birthday_str = ""
        for phone in self.phones:
            phones_info += f"{phone.value}, "
        if self.birthday:
            birthday_str = f"(Birthday at month {self.birthday.value[0:2]}, day {self.birthday.value[3:5]})"
        return f"{self.name.value.title()}{birthday_str}: {phones_info[:-2]}"

    def get_search(self):
        phones_info = ""
        birthday_str = ""
        for phone in self.phones:
            phones_info += f"{phone.value}, "
        if self.birthday:
            birthday_str = f"{self.birthday.value}"
        return f"{self.name.value.title()} {phones_info[:-2]} {birthday_str}"

    def delete_phone(self, delete_phone):
        old_len = len(self.phones)
        for phone in self.phones:
            if phone.value == delete_phone:
                self.phones.pop(self.phones.index(phone))
        if len(self.phones) == old_len:
            return False
        else:
            return True

    def change_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if phone.value == old_phone:
                self.delete_phone(old_phone)
                self.add_phone(new_phone)


class AddressBook(UserDict):

    def add_record(self, record):
        if record.name.value not in self.data:
            self.data[record.name.value] = record
        else:
            new_record = Record(record.name.value)
            exists_record = book.get_record(record.name.value)
            for phone in exists_record.phones:
                new_record.add_phone(phone.value)
            for phone in record.phones:
                new_record.add_phone(phone.value)
            if record.birthday:
                new_record.add_birthday(record.birthday.value)
            elif exists_record.birthday:
                new_record.add_birthday(exists_record.birthday.value)
            self.data[record.name.value] = new_record

    def get_all_record(self):
        return self.data

    def get_record(self, name) -> Record:
        return self.data.get(name)

    def has_record(self, name):
        return bool(self.data.get(name))

    def find_record(self, value):
        if self.has_record(value):
            return self.get_record(value)

        for record in self.get_all_record().values():
            for phone in record.phones:
                if phone.value == value:
                    return record

    def load_file(self):
        with open("saved_book.bin", "rb") as file:
            result = pickle.load(file)
        self.data.update(result)

    def save_file(self):
        with open("saved_book.bin", "wb") as file:
            pickle.dump(self.data, file)

    @staticmethod
    def iterator(phone_book):
        return Iterable(phone_book)

    def iterator_old(self, max_len=5):
        page = []
        i = 0
        for record in self.data.values():
            page.append(record)
            i += 1
            if i == max_len:
                yield page
                page = []
                i = 0
        if page:
            yield page

    def delete_record(self, name):
        del self.data[name]


class Iterable:

    def __init__(self, user_dict):
        self.iter_dict = user_dict.data
        self.current_value = 0
        self.iterable = iter(self.iter_dict)

    def __iter__(self):
        return self

    def __next__(self):
        if self.current_value < len(self.iter_dict):
            self.current_value += 1
            return self.iter_dict[next(self.iterable)]
        raise StopIteration


book = AddressBook()
iter_book = None


def input_error(func):  # decorator @input_error
    def inner_function(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except KeyError as e:
            result = f"Name {e} not found."
        except IndexError:
            result = "Phone number not entered."
        except TypeError:
            result = "Phone number not entered."
        except AttributeError:
            result = f"Name not found. Try again."
        except ValueError:
            result = f"Input correct information"
        except StopIteration:
            result = "--End--"
        finally:
            return result

    return inner_function


@input_error
def add_handler(user_input):
    if len(user_input) >= 2:
        record = Record(user_input[0])
        record.add_phone(user_input[1])
        book.add_record(record)
    return f"{str(user_input[0]).title()}: {user_input[1]} successfully added"


@input_error
def birthday_handler(user_input):
    if len(user_input) >= 2:
        if book.get_record(user_input[0]):
            record = book.get_record(user_input[0])
            date_str = f"{user_input[1]} {user_input[2]}"
            record.add_birthday(date_str)
            book.add_record(record)
            return f"{str(user_input[0]).title()}'s Birthday set at month {user_input[1]}, day {user_input[2]}"
        else:
            return f"Incorrect input. Enter 'Name Month(MM) Day(dd)'"
    else:
        return f"Name not found"


@input_error
def left_handler(user_input):
    if len(user_input) >= 1:
        record = book.get_record(user_input[0])
        return record.days_to_birthday()


@input_error
def change_handler(user_input):
    if len(user_input) >= 2:
        if user_input[0] == user_input[1]:
            return f"Its the same phone {user_input[1]}"
        elif book.find_record(user_input[0]):
            found_record = book.find_record(user_input[0])
            found_record.change_phone(user_input[0], user_input[1])
            book.delete_record(found_record.name.value)
            book.add_record(found_record)
            return f"Contact {found_record.name.value.title()}: old number {user_input[0]} " \
                   f"successfully changed to {user_input[1]}"
        else:
            return f"Phone {user_input[0]} no found"


@input_error
def delete_handler(user_input):
    if user_input[0]:
        book.delete_record(user_input[0])
        return f"Contact {user_input[0].title()} deleted"


def exit_handler(user_input):
    return "Good bye!"


def error_handler(user_input):
    return 'Command not found. Enter "help" for view command list.'


def hello_handler(user_input):
    return 'How can I help you?'


def help_handler(user_input):
    text = """ 
    "add" - add name(one word) and phone(digit): "add Ivan +380931234567"
    "birthday" - add date of birth by format MM DD: "birthday ivan 02 29"
    "close", "exit", "good bye" - exit from application: "exit"
    "change" - change old phone if exists to new phone: "change +380931234567 +380937654321"
    "delete", "remove" - delete contact: "delete Ivan"
    "hello" -  print How can I help you?: "hello"
    "help" - print help list: "help"
    "list" - get 5 records of address book, next input give next 5 records
    "left" - print day that left to birthday: "left ivan"
    "phone" - print phone or name: "search Ivan" or "search +380501234567"
    "page" - print names and phones with page count
    "search" - find and print all contacts if input match: "search 123"
    "show all" - print names and phones: "show all" """
    return text


def input_parser():
    input_list = []
    user_input = str(input("Enter: ")).lower()
    if not user_input.find(".") == -1:
        exit()
    else:
        user_input = user_input.strip()
        input_list = user_input.split(" ")

        if len(input_list) >= 2:

            if input_list[0] == "good" and input_list[1] == "bye":
                input_list[0] = input_list[0] + " " + input_list.pop(1)

            if input_list[0] == "show" and input_list[1] == "all":
                input_list[0] = input_list[0] + " " + input_list.pop(1)

        return input_list


@input_error
def pagination_old_handle(user_input):
    str_record = ""
    page_count = 1
    for page in book.iterator_old():
        str_record += f"---- Page № {page_count} ---\n"
        for record in page:
            str_record += f"{record.get_info()}\n"
        page_count += 1
        str_record += "\n"
    return str_record


@input_error
def pagination_handle(user_input):
    global iter_book
    iter_list = []
    if iter_book is None:
        iter_book = book.iterator(book)
    try:
        for i in range(5):
            iter_list.append(f"{next(iter_book).get_info()}")
    except Exception:
        iter_book = None
    finally:
        return "\n".join(iter_list)


@input_error
def phone_handler(user_input):
    if book.find_record(user_input[0].strip()):
        return book.find_record(user_input[0]).get_info()
    else:
        return f"{user_input[0]} not found"


def search_handler(user_input):
    find_data = ""
    if len(user_input):
        for record in book.get_all_record():
            if book.get(record).get_search().find(user_input[0]) != -1:
                find_data += f"{book.get(record).get_info()}\n"
    if not find_data:
        find_data = f"{user_input[0]} not found  "
    return find_data[:-2]


def show_handler(user_input):
    phone_book_list = []
    for key, rec in book.get_all_record().items():
        phone_book_list.append(rec.get_info())
    return "\n".join(phone_book_list)


HANDLER_DICT = {
    "add": add_handler,
    "birthday": birthday_handler,
    "close": exit_handler,
    "change": change_handler,
    "exit": exit_handler,
    "good bye": exit_handler,
    "hello": hello_handler,
    "help": help_handler,
    "left": left_handler,
    "list": pagination_handle,
    "page": pagination_old_handle,
    "phone": phone_handler,
    "remove": delete_handler,
    "search": search_handler,
    "show all": show_handler,
    "delete": delete_handler
}


def get_handler(operator):
    return HANDLER_DICT.get(operator, error_handler)


def main():
    try:
        book.load_file()
    except Exception:
        pass
    while True:
        user_input = input_parser()
        string = str(get_handler(user_input[0])(user_input[1:]))
        print(string)
        if string == "Good bye!":
            book.save_file()
            exit()


if __name__ == '__main__':
    main()
