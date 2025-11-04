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
    return (new_id, phone_book)


def find_contact(
    phone_book: PhoneBook, search_for: str, lookup_field: str = ''
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
    return (id, phone_book)


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


def prompt_save_file_option() -> bool | None:
    options = [
        ('Сохранить изменения', True),
        ('Продолжить без сохранения', False),
    ]

    return prompt_selection(options)


def prompt_repeat_save_dirty() -> bool:
    print_header('Контакты были изменены')

    while (should_save := prompt_save_file_option()) is None:
        print()

    return should_save


def prompt_for_number(prompt_text: str) -> int | None:
    print(prompt_text)
    if number := input('> ').strip():
        if number.isdigit():
            return int(number)

    return None


def prompt_for_string(prompt_text: str) -> str:
    print(prompt_text)
    return input('> ').strip()


def prompt_new_contact_fields() -> Contact | None:
    print('Введите имя')
    if not (name := input('> ').strip()):
        return

    print('Введите номер телефона')
    phone_number = input('> ').strip()

    print('Введите комментарий')
    comment = input('> ').strip()

    return {'name': name, 'phone_number': phone_number, 'comment': comment}


def prompt_update_contact_fields(contact: Contact) -> Contact:
    print(f"Введите имя ('{contact['name']}')")
    if not (name := input('> ').strip()):
        name = contact['name']

    print(f"Введите номер телефона ('{contact['phone_number']}')")
    if not (phone_number := input('> ').strip()):
        phone_number = contact['phone_number']

    print(f"Введите комментарий ('{contact['comment']}')")
    if not (comment := input('> ').strip()):
        comment = contact['comment']

    return {'name': name, 'phone_number': phone_number, 'comment': comment}


def prompt_lookup_field_option() -> str | None:
    print_header('Выберете поле для поиска')

    options = [
        ('Имя', 'name'),
        ('Телефон', 'phone_number'),
        ('Комментарий', 'comment'),
        ('* любое поле', ''),
    ]

    return prompt_selection(options)


def command_open(*, file_path: Path, dirty_flag: bool, **kwargs):
    if dirty_flag and prompt_repeat_save_dirty():
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


def command_create_contact(*, phone_book: PhoneBook, dirty_flag: bool, **kwargs):
    if contact := prompt_new_contact_fields():
        contact_id, phone_book = create_contact(phone_book, contact)
        dirty_flag = True
        print()
        print_header('Контакт создан')
        print_contact(contact_id, phone_book[contact_id])
        print('-' * 80)

    return {
        **kwargs,
        'phone_book': phone_book,
        'dirty_flag': dirty_flag,
    }


def command_find_contact(*, phone_book: PhoneBook, **kwargs):
    print_header('Найти контакт')
    print()

    if (lookup_field := prompt_lookup_field_option()) is not None:
        print()
        search_for = prompt_for_string('Введите строку для поиска')
        matching_contacts: PhoneBook = find_contact(
            phone_book, search_for, lookup_field
        )
        print()
        print_header(
            f'Найденные контакты ({len(matching_contacts)} из {len(phone_book)}):'
        )
        show_contacts(matching_contacts)

    return {**kwargs, 'phone_book': phone_book}


def command_update_contact(*, phone_book: PhoneBook, dirty_flag: bool, **kwargs):
    if (contact_id := prompt_for_number('Введите ID контакта')) and (
        contact_id in phone_book.keys()
    ):
        if contact := prompt_update_contact_fields(phone_book[contact_id]):
            contact_id, phone_book = update_contact(phone_book, contact_id, contact)
            dirty_flag = True
            print()
            print_header('Контакт изменён')
            print_contact(contact_id, phone_book[contact_id])
            print('-' * 80)

    return {
        **kwargs,
        'phone_book': phone_book,
        'dirty_flag': dirty_flag,
    }


def command_delete_contact(*, phone_book: PhoneBook, dirty_flag: bool, **kwargs):
    print_header('Удалить контакт')

    if (contact_id := prompt_for_number('Введите ID контакта')) and (
        contact_id in phone_book.keys()
    ):
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
    if dirty_flag and prompt_repeat_save_dirty():
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
            print()
            stop = True

        except Exception as e:
            print(f'Ошибка {e.__class__.__name__}: {e}')
            stop = False

        if stop:
            print('Bye!')
            break

        print()


if __name__ == '__main__':
    main()


# __EOF__
