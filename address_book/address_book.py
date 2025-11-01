# address_book/address_book.py

import json
from pathlib import Path
from typing import Any


type Id = int
type Contact = dict[str, Any]
type AddressBook = dict[Id, Contact]


def load_contacts(file_path: Path) -> AddressBook:
    with open(file_path) as file:
        book: AddressBook = json.load(file)
        return {int(id): contact for id, contact in book.items()}


def save_contacts(file_path: Path, address_book: AddressBook) -> None:
    with open(file_path, 'w') as file:
        json.dump(address_book, file, ensure_ascii=False, indent=4)


def show_contacts(address_book: AddressBook) -> None:
    for id, contact in address_book.items():
        print(f'[{id}]')
        for field, value in contact.items():
            print(f'{field}: {value}')
        print('-' * 80)


def create_contact(address_book: AddressBook, contact: Contact) -> AddressBook:
    new_id: Id = 1 + (max(address_book.keys()) if len(address_book) > 0 else 0)
    address_book[new_id] = contact
    return address_book


def find_contact(
    address_book: AddressBook, search_for: str, lookup_field: str | None = None
) -> AddressBook:
    search_result: AddressBook = {}
    for id, contact in address_book.items():
        for field, value in contact.items():
            if not lookup_field or field == lookup_field:
                if str(value).find(search_for) >= 0:
                    search_result[id] = contact
    return search_result


def update_contact(address_book: AddressBook, id: Id, contact: Contact) -> AddressBook:
    address_book[id] = contact
    return address_book


def delete_contact(address_book: AddressBook, id: Id) -> AddressBook:
    address_book.pop(id)
    return address_book


# __EOF__
