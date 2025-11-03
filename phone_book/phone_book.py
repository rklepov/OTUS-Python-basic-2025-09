#!/bin/env python3
#
# phone_book/phone_book.py
#

import json
from operator import itemgetter
from pathlib import Path
from typing import Any

type Id = int
type Contact = dict[str, Any]
type PhoneBook = dict[Id, Contact]


def print_contact(id: Id, contact: Contact) -> None:
    print(f'[{id}]')
    for field, value in contact.items():
        print(f'{field}: {value}')


def load_contacts(file_path: Path) -> PhoneBook:
    with open(file_path) as file:
        book: PhoneBook = json.load(file)
        return {int(id): contact for id, contact in book.items()}


def save_contacts(file_path: Path, phone_book: PhoneBook) -> None:
    with open(file_path, 'w') as file:
        json.dump(phone_book, file, ensure_ascii=False, indent=2)


def show_contacts(phone_book: PhoneBook) -> None:
    for id, contact in phone_book.items():
        print_contact(id, contact)
        print('-' * 80)


def create_contact(
    phone_book: PhoneBook, contact: Contact
) -> tuple[Contact, PhoneBook]:
    new_id: Id = 1 + (max(phone_book.keys()) if len(phone_book) > 0 else 0)
    phone_book[new_id] = contact
    return (contact, phone_book)


def find_contact(
    phone_book: PhoneBook, search_for: str, lookup_field: str | None = None
) -> PhoneBook:
    search_result: PhoneBook = {}
    for id, contact in phone_book.items():
        for field, value in contact.items():
            if not lookup_field or field == lookup_field:
                if str(value).find(search_for) >= 0:
                    search_result[id] = contact
    return search_result


def update_contact(
    phone_book: PhoneBook, id: Id, contact: Contact
) -> tuple[Contact, PhoneBook]:
    phone_book[id] = contact
    return (contact, phone_book)


def delete_contact(phone_book: PhoneBook, id: Id) -> tuple[Contact, PhoneBook]:
    deleted_contact: Contact = phone_book.pop(id)
    return (deleted_contact, phone_book)


def print_header(text: str) -> None:
    print(f'{text.capitalize()}')
    print('{0:-<{1}}'.format('', len(text)))


def prefer_relative_path(path: Path, other: Path) -> Path:
    if (abs_path := path.absolute()).is_relative_to(other):
        return abs_path.relative_to(other)
    return abs_path


def prompt_selection(menu: list[str, Any]) -> Any:
    for n, (prompt, _) in enumerate(menu):
        print(f'({n + 1}): {prompt}')

    print()

    action = None

    if (selection := input('> ').strip()).isdigit():
        if 0 < (item := int(selection)) <= len(menu):
            _, action = menu[item - 1]

    return action


def prompt_file_path_or_default(default_path: Path) -> Path:
    relative_path = prefer_relative_path(default_path, Path.cwd())

    print(f'Введите имя файла ({relative_path})')

    if file_path := input('> ').strip():
        return Path(file_path)

    return default_path


def prompt_save_file_option() -> bool:
    options = [
        ('Сохранить изменения', True),
        ('Продолжить без сохранения', False),
    ]

    return prompt_selection(options)


def prompt_save_dirty_option() -> bool:
    print_header('Контакты были изменены')
    return prompt_save_file_option()


def prompt_contact_id() -> int | None:
    print('Введите ID контакта')
    if contact_id := input('> ').strip():
        if contact_id.isdigit():
            return int(contact_id)

    return None


def command_open(*, file_path: Path, dirty_flag: bool, **kwargs):
    if dirty_flag and prompt_save_dirty_option():
        print()
        command_save(file_path=file_path, dirty_flag=dirty_flag, **kwargs)
        print()

    print_header('Загрузить телефонный справочник из файла')

    file_path = prompt_file_path_or_default(file_path)
    phone_book = load_contacts(file_path)

    return {
        **kwargs,
        'phone_book': phone_book,
        'file_path': file_path,
        'dirty_flag': False,
    }


def command_save(*, phone_book: PhoneBook, file_path: Path, **kwargs):
    print_header('Сохранить телефонный справочник в файл')

    file_path = prompt_file_path_or_default(file_path)

    save_contacts(file_path, phone_book)

    return {
        **kwargs,
        'phone_book': phone_book,
        'file_path': file_path,
        'dirty_flag': False,
    }


def command_show_contacts(*, phone_book: PhoneBook, **kwargs):
    print_header(f'Контакты ({len(phone_book)}):')

    show_contacts(phone_book)

    return {
        **kwargs,
        'phone_book': phone_book,
    }


def command_create_contact(*, phone_book: PhoneBook, **kwargs):
    return {
        **kwargs,
        'phone_book': phone_book,
        'dirty_flag': True,
    }


def command_find_contact(*, phone_book: PhoneBook, **kwargs):
    return {**kwargs, 'phone_book': phone_book}


def command_update_contact(*, phone_book: PhoneBook, **kwargs):
    return {
        **kwargs,
        'phone_book': phone_book,
        'dirty_flag': True,
    }


def command_delete_contact(*, phone_book: PhoneBook, dirty_flag: bool, **kwargs):
    print_header('Удалить контакт')

    if (contact_id := prompt_contact_id()) and (contact_id in phone_book.keys()):
        deleted_contact, phone_book = delete_contact(phone_book, contact_id)
        dirty_flag = True
        print()
        print_header('Контакт удалён')
        print_contact(contact_id, deleted_contact)

    return {
        **kwargs,
        'phone_book': phone_book,
        'dirty_flag': dirty_flag,
    }


def command_exit(*, phone_book: PhoneBook, file_path: Path, dirty_flag: bool, **kwargs):
    if dirty_flag and prompt_save_dirty_option():
        print()
        kwargs = command_save(
            phone_book=phone_book, file_path=file_path, dirty_flag=dirty_flag, **kwargs
        )
    else:
        kwargs = {
            **kwargs,
            'phone_book': phone_book,
            'file_path': file_path,
            'dirty_flag': dirty_flag,
        }

    print()

    return {**kwargs, 'stop': True}


def main_menu(file_path: Path, dirty_flag: bool, count_contacts: int):
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

    print_header(
        f'Телефонный справочник'
        f' [{prefer_relative_path(file_path, Path.cwd())}{" *" if dirty_flag else ""}]'
        f' ({count_contacts})'
    )

    command = prompt_selection(main_menu)

    return command


def main():
    phone_book: PhoneBook = {}
    file_path: str = Path(__file__).resolve().parent / f'{Path(__file__).stem}.json'
    dirty_flag = False
    stop = False

    if Path.exists(file_path):
        try:
            phone_book = load_contacts(file_path)
        except OSError as e:
            print(
                '[WARN] Невозможно загрузить телефонный справочник из файла'
                f' "{prefer_relative_path(file_path, Path.cwd())}":'
                f' {e}'
            )
            print()

    while True:
        try:
            command = main_menu(file_path, dirty_flag, len(phone_book))
            print()

            kwargs = {
                'phone_book': phone_book,
                'file_path': file_path,
                'dirty_flag': dirty_flag,
                'stop': stop,
            }

            if not command:
                continue

            phone_book, file_path, dirty_flag, stop = itemgetter(
                'phone_book', 'file_path', 'dirty_flag', 'stop'
            )(command(**kwargs))

        except (KeyboardInterrupt, EOFError) as e:
            print()
            print(f'Исполнение прервано: {e.__class__.__name__}')
            stop = True

        except Exception as e:
            print(f'Ошибка {e.__class__.__name__}: {e}')
            stop = False

        print()

        if stop:
            print('Bye!')
            break


if __name__ == '__main__':
    main()


# __EOF__
