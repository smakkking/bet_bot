import os
import sys

# путь к папке bet_bot
BET_PROJECT_ROOT    = r'C:\GitRep\bet_bot'

# путь к папке, где хранятся chrome данные(диркетории + профили)
CHROME_DIR_PACKAGES = r'C:\Users\user1\AppData\Local\Google\Chrome'

# путь к файлу с инфой о всех последних постах
ALL_POSTS_JSON_PATH = BET_PROJECT_ROOT + r'\user_data\group_post_data.json'

sys.path.append(BET_PROJECT_ROOT)


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web_part.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
