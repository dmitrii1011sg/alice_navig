import random
from flask import Flask, request
import logging
import json
from config import *
from my_tools import get_poem_with_author

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)


def separation_line(text, num_simbols, index_start_line) -> tuple:
    text_lines = text.split('\n')[index_start_line:]
    result_text_lines = list()
    for index_line, line in enumerate(text_lines):

        if len('\n'.join(result_text_lines)) + len(line) + 1 < num_simbols:
            result_text_lines.append(line)

        elif len('\n'.join(result_text_lines)) + len(line) + 1 >= num_simbols:
            return '\n'.join(result_text_lines), index_line + index_start_line + 1

    return '\n'.join(result_text_lines), -1


def slice_lines(text, num_lines, index_start_line):
    text_lines = text.split('\n')
    len_lines = len(text_lines) - 1
    if len_lines > index_start_line + num_lines - 1:
        result_text_lines = text_lines[index_start_line:index_start_line + num_lines]
        return '\n'.join(result_text_lines), index_start_line + num_lines
    else:
        result_text_lines = text_lines[index_start_line:]
        return '\n'.join(result_text_lines), -1

def clear_value(value):
    return {
            "mode": value['mode'],
            "read": {
                'name_author': False,
                'title_poem': False,
                'next_string': 0
            },
            "learn": {
                'name_author': False,
                'title_poem': False,
                'next_string': 0,
                'next_string_suggest': 0
            }
        }


def created_response(version, session, text, value=False, end=False) -> dict:
    """
    Created response for Alice

    :param version: version
    :param session: config session
    :param text: text for Alice
    :param value: value for safe storage
    :param end: True - end session, False - continue session
    :return: dict
    """
    response = {
        "version": version,
        "session": session,
        "response": {
            "end_session": end,
            "text": text
        },
        "session_state": {
            "value": value
        },
    }
    return response

@app.route("/", methods=["POST", "GET"])
def main(req, *context):
    """
    req["session"]["new"] - checking for a new session
    req["request"]["original_utterance"] - user response
    req["state"]["session"]["value"] - 'safe storage' value (not working)

    :return: None
    """
    logging.info(request.json)
    req = request.json
    end = False
    text = 'Error'

    if req["session"]["new"]:  # если пользователь не впервые
        text = 'Приветствую Вас в навыке "Хранитель стихотворений". Вы уже знакомы с тем, что я умею?'
        value = {
            "mode": "start",
            "read": {
                'name_author': False,
                'title_poem': False,
                'next_string': 0
            },
            "learn": {
                'name_author': False,
                'title_poem': False,
                'next_string': 0,
                'next_string_suggest': 0
            }
        }

    elif req["request"]["original_utterance"].lower() in exit_commands:  # exit
        text = 'До скорых встреч. Пока.'
        end = True

    elif req["request"]["original_utterance"].lower() in readPoem_commands:
        value = req["state"]["session"]["value"]
        text = f"{random.choice(['Супер!', 'Хорошо!'])} Назовите фамилию автора и название стихотворения."
        value["mode"] = "change_author_title_poem_read"

    elif req["request"]["original_utterance"].lower() in learnPoem_commands:
        value = req["state"]["session"]["value"]
        text = f"{random.choice(['Супер!', 'Хорошо!'])} Назовите фамилию автора и название стихотворения."
        value["mode"] = "change_author_title_poem_learn"

    elif req['request']['original_utterance'].lower() in help_command:
        value = req["state"]["session"]["value"]
        text = """Я могу помочь в выучивании стихотворения, достаточно сказать "давай выучим стихотворение", а также Вы можете скоротать вечер, наслаждаясь моим чтением, просто скажите "давай прочитаем стихотворение".\n
                Иногда во время чтения я буду давать Вам возможность обдумать прочитанное. Достаточно сказать "продолжаем", и я продолжу чтение стихотворения.
                Теперь, после того как я рассказала вам о себе, ответье на мой предыдущий вопрос, пожалуйста."""

    elif req["state"]["session"]["value"]["mode"] == "start":
        value = req["state"]["session"]["value"]
        if req["request"]["original_utterance"].lower() in agreement_commands:
            text = f"Итак, что будем делать {random.choice(['сегодня?', 'в этот раз?', 'на сей раз?'])}"
            value['mode'] = 'change_mode'
        elif req["request"]["original_utterance"].lower() in disagreement_commands:
            text = """Что ж, пора с вами поделиться легендарным сказом о данном навыке.\n
                        Он может помочь в выучивании стихотворения, достаточно сказать "давай выучим стихотворение", а также Вы можете скоротать вечер, наслаждаясь моим чтением, просто скажите "давай прочитаем стихотворение".\n
                        Иногда во время чтения я буду давать Вам возможность обдумать прочитанное. Достаточно сказать "продолжаем", и я продолжу чтение стихотворения. """
            value['mode'] = 'tutorial_start'
        else:
            text = """Я, к сожалению, не поняла, что вы хотели сказать, повторите пожалуйста."""

    elif req["state"]["session"]["value"]["mode"] == "tutorial_start":
        text = f"Итак, что будем делать {random.choice(['сегодня?', 'в этот раз?', 'на сей раз?'])}"
        value = req["state"]["session"]["value"]
        value['mode'] = 'change_mode'

    elif req["state"]["session"]["value"]["mode"] == "change_mode":
        value = req["state"]["session"]["value"]
        if req["request"]["original_utterance"].lower() in readPoem_commands:
            text = f"{random.choice(['Супер!', 'Хорошо!'])} Назовите фамилию автора и название стихотворения."
            value["mode"] = "change_author_title_poem_read"
        elif req["request"]["original_utterance"].lower() in learnPoem_commands:
            text = f"{random.choice(['Супер!', 'Хорошо!'])} Назовите фамилию автора и название стихотворения."
            value["mode"] = "change_author_title_poem_learn"
        else:
            text = """Я, к сожалению, не поняла, что вы хотели сказать, повторите пожалуйста."""

    elif req["state"]["session"]["value"]["mode"] == "change_author_title_poem_read":
        text_user = req["request"]["original_utterance"]
        name_author = text_user.split()[0]
        title_poem = ' '.join(text_user.split()[1:])
        text_poem = get_poem_with_author(name_author, title_poem)
        value = req["state"]["session"]["value"]
        if text_poem is None:  # Если не нашлось
            text = f"Очень жаль, но я не знаю стихотворение: {text_user}.\nНазовите, пожалуйста, другое стихотворение."
        if text_poem:
            text = 'Я знаю такое стихотворение!\nСкажите любое слово чтобы продолжить.'
            value['mode'] = 'read'
            value['read']['name_author'] = name_author
            value['read']['title_poem'] = title_poem
            value['read']['next_string'] = 0

    elif req["state"]["session"]["value"]["mode"] == "read":  # чтение
        value = req["state"]["session"]["value"]
        name_author = value['read']['name_author']
        title_poem = value['read']['title_poem']
        text_poem = get_poem_with_author(name_author, title_poem)

        text, next_string = separation_line(text_poem, 900, value['read']["next_string"])
        if next_string == -1:
            text += f"\n ...{random.choice(['Замечательное', 'Восхитительное', 'Хорошое', 'Красивое'])} стихотворение! Продолжим нашу работу?"
            value['mode'] = "repeat_read"
        else:
            text += "\n ...Скажите что нибудь для продолжения."
            value['read']['next_string'] = next_string

    elif req["state"]["session"]["value"]["mode"] == "repeat_read":
        value = req["state"]["session"]["value"]
        if req["request"]["original_utterance"].lower() in agreement_commands:
            text = f"{random.choice(['Прекрасно! Желаете выучить стихотворение, или прослушать его?', 'Рада слышать! Хотите прослушать стихотворение, или выучить его?'])}"
            value["mode"] = "change_mode"
            value = clear_value(value)
        elif req["request"]["original_utterance"].lower() in disagreement_commands:
            text = "Хорошо, была рада читать для вас! До скорой встречи."
            value = clear_value(value)
            end = True
        else:
            text = """Я, к сожалению, не поняла, что вы хотели сказать, повторите пожалуйста."""

    elif req["state"]["session"]["value"]["mode"] == "change_author_title_poem_learn":
        text_user = req["request"]["original_utterance"]
        name_author = text_user.split()[0]
        title_poem = ' '.join(text_user.split()[1:])
        text_poem = get_poem_with_author(name_author, title_poem)
        value = req["state"]["session"]["value"]
        if text_poem is None:  # Если не нашлось
            text = f"Очень жаль, но я не знаю стихотворение: {text_user}.\nНазовите, пожалуйста, другое стихотворение."
        if text_poem:
            text = """Я знаю такое стихотворение!
                        Говорите "еще", пока не выучите 2 строки. Как только запомните их, скажите "далее", и я перейду к следующим двум.
                        Если вы устали, то скажите "хватит".
                        Скажите "Начать" для перехода к изучению."""
            value['mode'] = 'learn'
            value['learn']['name_author'] = name_author
            value['learn']['title_poem'] = title_poem
            value['learn']['next_string'] = 0

    elif req["state"]["session"]["value"]["mode"] == 'learn':
        value = req["state"]["session"]["value"]
        text_user = req["request"]["original_utterance"].lower()

        if text_user in addition_command:
            name_author = value['learn']['name_author']
            title_poem = value['learn']['title_poem']
            text_poem = get_poem_with_author(name_author, title_poem)

            text, next_string = slice_lines(text_poem, 2, value['learn']["next_string"])
            value['learn']['next_string_suggest'] = next_string

        elif text_user in next_command:
            name_author = value['learn']['name_author']
            title_poem = value['learn']['title_poem']
            text_poem = get_poem_with_author(name_author, title_poem)

            if value['learn']["next_string_suggest"] != -1:
                text, next_string = slice_lines(text_poem, 2, value['learn']["next_string_suggest"])
                value['learn']['next_string'] = value['learn']["next_string_suggest"]
                value['learn']['next_string_suggest'] = next_string
            elif value['learn']["next_string_suggest"] == -1:
                text = "Вы довольны тем, насколько вы выучили этот фрагмент стихотворения?"
                value['mode'] = 'repeat_learn'

        elif text_user in stop_command:
            text = f"{random.choice(['Желаете выучить ещё стихотворение, или прослушать?', 'Хотите прослушать ещё стихотворение, или выучить?'])}"
            value['mode'] = 'repeat_read'
            value = clear_value(value)
        else:
            text = """Я, к сожалению, не поняла, что вы хотели сказать, повторите пожалуйста."""

    elif req["state"]["session"]["value"]["mode"] == 'repeat_learn':
        value = req["state"]["session"]["value"]
        text_user = req["request"]["original_utterance"].lower()

        if req["request"]["original_utterance"].lower() in agreement_commands:
            text = f"{random.choice(['Прекрасно! Желаете выучить стихотворение, или прослушать его?', 'Рада слышать! Хотите прослушать стихотворение, или выучить его?'])}"
            value["mode"] = "change_mode"
            value = clear_value(value)
        elif req["request"]["original_utterance"].lower() in disagreement_commands:
            text = 'Тогда повторим. Скажите "Начать" для перехода к изучению.'
            value['mode'] = 'learn'
            value['learn']['next_string'] = 0
            value['learn']['next_string_suggest'] = 2
        else:
            text = """Я, к сожалению, не поняла, что вы хотели сказать, повторите пожалуйста."""

    response = created_response(req["version"], req["session"], text=text, value=value, end=end)
    return response


if __name__ == '__main__':
    app.run(debug=True)

