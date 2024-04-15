'''from gtts import gTTS
import os
import pygame
import logging

class TextToSpeech:
    """
    A class that represents a text-to-speech converter.
    """

    def __init__(self):
        """
        Initialize the logger.
        """
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    def speak(self, text):
        """
        Convert the given text to speech.
        """
        try:
            self.logger.info(f"Speaking the text: {text}")
            tts = gTTS(text=text, lang='en')
            tts.save("speech.mp3")
            pygame.mixer.init()
            pygame.mixer.music.load("speech.mp3")
            pygame.mixer.music.play()
            pygame.event.wait()  # Wait for playback to finish
            os.remove("speech.mp3")
            tts.save("speech.mp3")
            os.system("mpg321 speech.mp3")
            os.remove("speech.mp3")
        except Exception as exception:
            self.logger.error(f"An error occurred while trying to speak the text: {str(exception)}")
            raise'''

from gtts import gTTS
import os
import pygame
import logging

class TextToSpeech:
    """
    A class that represents a text-to-speech converter.
    """

    def __init__(self):
        """
        Initialize the logger.
        """
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    def speak(self, text):
        """
        Convert the given text to speech.
        """
        try:
            self.logger.info(f"Speaking the text: {text}")
            tts = gTTS(text=text, lang='en')
            tts.save("speech.mp3")

            # Initialize pygame mixer
            pygame.mixer.init()

            # Load the saved speech
            pygame.mixer.music.load("speech.mp3")

            # Play the speech
            pygame.mixer.music.play()

            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

            # Stop and quit pygame mixer
            pygame.mixer.music.stop()
            pygame.mixer.quit()

            # Remove the temporary speech file
            os.remove("speech.mp3")

        except Exception as exception:
            self.logger.error(f"An error occurred while trying to speak the text: {str(exception)}")
            raise
