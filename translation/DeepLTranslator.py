# import Translator
from typing import Optional, List
import time
from pynput.mouse import Button, Controller
from pynput.keyboard import Key, Controller
import random
import pynput
import webbrowser
import pyperclip

from src.translation.Translator import Translator as Base


class DeepLTranslator(Base):
    def __init__(self):
        super().__init__()
        self.name = 'DeepL'

    def do_translate(self, data: List[str], src: Optional[str], dest: Optional[str]):
        keyboard = pynput.keyboard.Controller()
        mouse = pynput.mouse.Controller()

        """
        DELIMITER = random.choice(["!!!!", "????", '----', '////'])

        content = DELIMITER.join(data)

        webbrowser.open("https://www.deepl.com/en/translator#"+src+"/"+dest+"/")
        time.sleep(2)

        pyperclip.copy(content)

        keyboard.press(Key.ctrl.value)
        keyboard.press('v')
        keyboard.release(Key.ctrl.value)
        keyboard.release('v')
        time.sleep(10)

        mouse.position = (1200, 600)
        mouse.press(Button.left)
        mouse.release(Button.left)
        time.sleep(1)
        mouse.position = (1200, 600)
        mouse.click(Button.left, 2)
        time.sleep(1)

        keyboard.press(Key.ctrl.value)
        keyboard.press('a')
        keyboard.release(Key.ctrl.value)
        keyboard.release('a')
        time.sleep(1)

        keyboard.press(Key.ctrl.value)
        keyboard.press('c')
        keyboard.release(Key.ctrl.value)
        keyboard.release('c')

        time.sleep(1)

        translated_content = pyperclip.paste()
        results = translated_content.split(DELIMITER)

        if len(results) != len(data):
            print('Length error', len(results), len(data))
            raise Exception

        for i in range(len(results)):
            results[i] = results[i].strip()

        time.sleep(2+random.randint(0, 1))
        return results
        """

        results = []
        webbrowser.open("https://www.deepl.com/en/translator#" + src + "/" + dest + "/")
        time.sleep(1)

        for i in range(len(data)):
            pyperclip.copy(data[i])

            # exit(0)

            mouse.position = (240, 490)
            mouse.press(Button.left)
            mouse.release(Button.left)
            time.sleep(1)
            mouse.position = (240, 490)
            mouse.click(Button.left, 2)
            time.sleep(1)

            keyboard.press(Key.ctrl.value)
            keyboard.press('a')
            keyboard.release(Key.ctrl.value)
            keyboard.release('a')
            time.sleep(1)

            keyboard.press(Key.backspace.value)
            keyboard.release(Key.backspace.value)
            time.sleep(1)

            keyboard.press(Key.ctrl.value)
            keyboard.press('v')
            keyboard.release(Key.ctrl.value)
            keyboard.release('v')

            time.sleep(3)

            # exit(0)

            mouse.position = (1150, 490)
            mouse.press(Button.left)
            mouse.release(Button.left)
            time.sleep(1)
            mouse.position = (1150, 490)
            mouse.click(Button.left, 2)
            time.sleep(1)

            keyboard.press(Key.ctrl.value)
            keyboard.press('a')
            keyboard.release(Key.ctrl.value)
            keyboard.release('a')
            time.sleep(1)

            keyboard.press(Key.ctrl.value)
            keyboard.press('c')
            keyboard.release(Key.ctrl.value)
            keyboard.release('c')

            time.sleep(1)

            translated_content = pyperclip.paste()
            translated_content = translated_content.replace(
                "\n\nTranslated with www.DeepL.com/Translator (free version)", "")
            results.append(translated_content)

        time.sleep(3)
        return results
