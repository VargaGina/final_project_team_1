from datetime import datetime, timedelta
from joblib import dump, load
import re

class PersonalAssistant:
    def __init__(self):
        self.contacts_file = "contacts.joblib"
        self.notes_file = "notes.txt"
        self.contacts = self.load_data(self.contacts_file)
        self.notes = self.load_notes()

    def load_data(self, file_name):
        try:
            return load(file_name)
        except FileNotFoundError:
            return {}

    def load_notes(self):
        try:
            with open(self.notes_file, "r") as file:
                return file.readlines()
        except FileNotFoundError:
            return []

    def save_data(self, data, file_name):
        try:
            dump(data, file_name)
        except Exception as e:
            print(f"Error saving data: {e}")

    def save_notes(self):
        try:
            with open(self.notes_file, "w") as file:
                file.writelines(self.notes)
        except Exception as e:
            print(f"Error saving notes: {e}")

    def add_contact(self, name, address, phone, email, birthday):
        try:
            datetime.strptime(birthday, "%Y-%m-%d")
        except ValueError:
            return "Invalid birthday format. Please use YYYY-MM-DD."

        if not self.validate_phone(phone):
            return "Invalid phone number format."
        if not self.validate_email(email):
            return "Invalid email format."

        self.contacts[name] = {"address": address, "phone": phone, "email": email, "birthday": birthday}
        self.save_data(self.contacts, self.contacts_file)
        return f"Contact {name} added."

    def search_contact(self, query):
        result = []
        for name, contact in self.contacts.items():
            if query.lower() in name.lower():
                result.append((name, contact))
        return result

    def display_upcoming_birthdays(self, days):
        today = datetime.now()
        upcoming_birthdays = []
        for name, contact in self.contacts.items():
            birthday = datetime.strptime(contact["birthday"], "%Y-%m-%d")
            birthday_this_year = birthday.replace(year=today.year)

            
            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)

            if 0 <= (birthday_this_year - today).days <= days:
                upcoming_birthdays.append((name, birthday_this_year))
        return upcoming_birthdays

    def validate_phone(self, phone):
        return phone.isdigit() and len(phone) == 10

    def validate_email(self, email):
        return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None
    
    def add_note(self, note):
        self.notes.append(note + "\n")
        self.save_notes()
        return "Note added."

    def search_note(self, query):
        matching_notes = [note for note in self.notes if query.lower() in note.lower()]
        return matching_notes
    
    def delete_note(self, note):
        if note + "\n" in self.notes:
            self.notes.remove(note + "\n")
            self.save_notes()
            return True
        return False

    def delete_contact(self, name):
        if name in self.contacts:
            del self.contacts[name]
            self.save_data(self.contacts, self.contacts_file)
            return True
        return False
    

    def edit_contact(self, name, field, value):
        if name in self.contacts:
            if field in self.contacts[name]:
                if field == 'phone' and not self.validate_phone(value):
                    return "Invalid phone number format. "
                elif field == 'email' and not self.validate_email(value):
                    return "Invalid email format. "
                elif field == 'birthday':
                    try:
                        datetime.strptime(value, "%Y-%m-%d")
                    except ValueError:
                        return "Invalid birthday format. "
                self.contacts[name][field] = value
                self.save_data(self.contacts, self.contacts_file)
                return f"Contact {name} {field} updated to {value}."
            else:
                return "Invalid field."
        else:
            return "Contact not found."

    def edit_note(self, index, new_note):
        if 0 <= index < len(self.notes):
            self.notes[index] = new_note + "\n"
            self.save_notes()
            return "Note updated."
        else:
            return "Invalid note index."

def parse_input(user_input):
    parts = user_input.strip().split(maxsplit=1)
    command = parts[0].lower()
    args = parts[1].split(',') if len(parts) > 1 else []
    return command, [arg.strip() for arg in args]

def main():
    pa = PersonalAssistant()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
       

        elif command == "add_contact":
            if len(args) == 5:
                name, address, phone, email, birthday = args
                result = pa.add_contact(name, address, phone, email, birthday)
                print(result)
            else:
                print("Usage: add_contact <name>, <address>, <phone>, <email>, <birthday>")
        elif command == "search_contact":
            if len(args) == 1:
                results = pa.search_contact(args[0])
                if results:
                    for name, contact in results:
                        print(f"Name: {name}, Address: {contact['address']}, Phone: {contact['phone']}, Email: {contact['email']}, Birthday: {contact['birthday']}")
                else:
                    print("No contacts found.")
            else:
                print("Usage: search_contact <query>")
        elif command == "upcoming_birthdays":
            if len(args) == 1 and args[0].isdigit():
                results = pa.display_upcoming_birthdays(int(args[0]))
                if results:
                    for name, birthday in results:
                        print(f"Name: {name}, Birthday: {birthday.strftime('%Y-%m-%d')}")
                else:
                    print("No upcoming birthdays.")
            else:
                print("Usage: upcoming_birthdays <days>")
        elif command == "add_note":
            if len(args) == 1:
                result = pa.add_note(args[0])
                print(result)
            else:
                print("Usage: add_note <note>")
        elif command == "search_note":
            if len(args) == 1:
                results = pa.search_note(args[0])
                if results:
                    for note in results:
                        print(note.strip())
                else:
                    print("No notes found.")
            else:
                print("Usage: search_note <query>")
        elif command == "delete_contact":
            if len(args) == 1:
                if pa.delete_contact(args[0]):
                    print(f"Contact {args[0]} deleted.")
                else:
                    print("Contact not found.")
            else:
                print("Usage: delete_contact <name>")
        elif command == "delete_note":
            if len(args) == 1:
                if pa.delete_note(args[0]):
                    print("Note deleted.")
                else:
                    print("Note not found.")
            else:
                print("Usage: delete_note <note>")
        elif command == "edit_contact":
            if len(args) == 3:
                name, field, value = args
                result = pa.edit_contact(name, field, value)
                print(result)
            else:
                print("Usage: edit_contact <name>, <field>, <value>")
        elif command == "edit_note":
            if len(args) == 2 and args[0].isdigit():
                index, new_note = int(args[0]), args[1]
                result = pa.edit_note(index, new_note)
                print(result)
            else:
                print("Usage: edit_note <index>, <new_note>")
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
