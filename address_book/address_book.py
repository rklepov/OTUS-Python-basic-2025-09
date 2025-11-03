#!/bin/env python3
#
# address_book/address_book.py
#

import json
from operator import itemgetter
from pathlib import Path
from typing import Any

type Id = int
type Contact = dict[str, Any]
type AddressBook = dict[Id, Contact]


def print_contact(id: Id, contact: Contact) -> None:
    print(f'[{id}]')
    for field, value in contact.items():
        print(f'{field}: {value}')


def load_contacts(file_path: Path) -> AddressBook:
    with open(file_path) as file:
        book: AddressBook = json.load(file)
        return {int(id): contact for id, contact in book.items()}


def save_contacts(file_path: Path, address_book: AddressBook) -> None:
    with open(file_path, 'w') as file:
        json.dump(address_book, file, ensure_ascii=False, indent=4)


def show_contacts(address_book: AddressBook) -> None:
    print(f'Контакты ({len(address_book)}):')
    print('-' * 80)
    for id, contact in address_book.items():
        print('-' * 80)
        print_contact(id, contact)
    print('-' * 80)


def create_contact(
    address_book: AddressBook, contact: Contact
) -> tuple[Contact, AddressBook]:
    new_id: Id = 1 + (max(address_book.keys()) if len(address_book) > 0 else 0)
    address_book[new_id] = contact
    return (contact, address_book)


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


def update_contact(
    address_book: AddressBook, id: Id, contact: Contact
) -> tuple[Contact, AddressBook]:
    address_book[id] = contact
    return (contact, address_book)


def delete_contact(address_book: AddressBook, id: Id) -> tuple[Contact, AddressBook]:
    deleted_contact: Contact = address_book.pop(id)
    return (deleted_contact, address_book)


def prompt_selection(menu: list[str, Any]) -> Any:
    for n, (prompt, _) in enumerate(menu):
        print(f'({n + 1}): {prompt}')

    print()

    action = None

    if (selection := input('> ').strip()).isdigit():
        if 0 < (item := int(selection)) <= len(menu):
            _, action = menu[item - 1]

    return action


def command_open(*, file_path: Path, **kwargs):
    return {
        **kwargs,
        'file_path': file_path,
        'dirty_flag': False,
    }


def command_save(*, address_book: AddressBook, file_path: Path, **kwargs):
    return {
        **kwargs,
        'address_book': address_book,
        'file_path': file_path,
        'dirty_flag': False,
    }


def command_show_contacts(*, address_book: AddressBook, **kwargs):
    show_contacts(address_book)
    return {
        **kwargs,
        'address_book': address_book,
    }


def command_create_contact(*, address_book: AddressBook, **kwargs):
    return {
        **kwargs,
        'address_book': address_book,
        'dirty_flag': True,
    }


def command_find_contact(*, address_book: AddressBook, **kwargs):
    return {**kwargs, 'address_book': address_book}


def command_update_contact(*, address_book: AddressBook, **kwargs):
    return {
        **kwargs,
        'address_book': address_book,
        'dirty_flag': True,
    }


def command_delete_contact(*, address_book: AddressBook, **kwargs):
    return {
        **kwargs,
        'address_book': address_book,
        'dirty_flag': True,
    }


def command_exit(**kwargs):
    return {**kwargs, 'stop': True}


def main_menu():
    main_menu = [
        ('Открыть из файла', command_open),
        ('Сохранить в файл', command_save),
        ('Показать все контакты', command_show_contacts),
        ('Создать контакт', command_create_contact),
        ('Найти контакт', command_find_contact),
        ('Изменить контакт', command_update_contact),
        ('Удалить контакт', command_delete_contact),
        ('Выход', command_exit),
    ]

    print('Телефонный справочник')
    print('---------------------')

    command = prompt_selection(main_menu)

    return command


def main():
    address_book: AddressBook = {}
    file_path: str = Path(__file__).resolve().parent / f'{Path(__file__).stem}.json'
    dirty_flag = False
    stop = False

    while True:
        try:
            command = main_menu()
            print()

            kwargs = {
                'address_book': address_book,
                'file_path': file_path,
                'dirty_flag': dirty_flag,
                'stop': stop,
            }

            if not command:
                continue

            address_book, file_path, dirty_flag, stop = itemgetter(
                'address_book', 'file_path', 'dirty_flag', 'stop'
            )(command(**kwargs))

        except (KeyboardInterrupt, EOFError) as e:
            print()
            print(f'Исполнение прервано: {e.__class__.__name__}')
            stop = True

        except Exception as e:
            print(f'Ошибка ({e.__class__.__name__}): {e}')
            stop = False

        print()

        if stop:
            print('Bye!')
            break


if __name__ == '__main__':
    main()


# __EOF__
