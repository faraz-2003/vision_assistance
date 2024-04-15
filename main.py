from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image,AsyncImage
from kivy.uix.camera import Camera
from kivy.graphics.texture import Texture
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from logger import Logger
from gemini_vision import GeminiVision
from speech import SpeechToText
from voice import TextToSpeech
import cv2
import numpy as np
from PIL import Image as ig
from PIL import PngImagePlugin
from kivy.core.window import Window
from kivy.graphics import Rectangle
from kivy.core.audio import SoundLoader

class YourKivyApp(App):
    def __init__(self, **kwargs):
        super(YourKivyApp, self).__init__(**kwargs)
        self.logger = Logger.get_logger('gemini_vision_pro.log')
        self.api_key = 'AIzaSyDHwJ55h9cl3ZBuXEEKOfwAL4nN1PfdoRY' #AIzaSyAhj0U2x_6dU9ng_strnaGl_ifrN-rIuoY'  # Set your API key here
        self.temperature = 0.1
        self.top_k = 32
        self.top_p = 1.0
        self.gemini_vision = GeminiVision(self.api_key, self.temperature, self.top_p, self.top_k)
        self.tts = TextToSpeech()
        self.stt = SpeechToText()
        self.camera_access_granted = True  # Flag to control camera access
        self.captured_image = None
        self.prompt = ''
        self.image_widget = Image(size=(300, 300))
        self.sound1 = SoundLoader.load('shutter_sound.mp3')
        self.sound2 = SoundLoader.load('prompt_sound.wav')
        self.sound3 = SoundLoader.load('ask_sound.wav')
        self.gemini_response=None
        self.cancel_button = Button(size_hint=(None, None), size=(50, 50), background_normal='close_icon.jpg')
        self.cancel_button.bind(on_press=self.close_app)
    
    def build(self):
        layout = BoxLayout(orientation='vertical')
        top_layout = BoxLayout(size_hint=(1, None), height=50)
        top_layout.add_widget(Widget())
        top_layout.add_widget(self.cancel_button)
        layout.add_widget(top_layout)

        with layout.canvas.before:
            self.rect = Rectangle(source='background.png', pos=layout.pos, size=layout.size)

        layout.bind(size=self.update_rect)

        heading = Label(text='Assistance for Visually Impaired', font_size='35sp', size_hint_y=None, height=80)
        heading.pos_hint = {'center_x': 0.5}
        layout.add_widget(heading)

        # BoxLayout to contain the heading and images side by side
        image_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.6),spacing=40,padding=[40, 40, 40, 40])
        layout.add_widget(image_layout)

        layout.add_widget(Widget(size_hint_y=None, height=20))

        # Webcam streamer
        self.camera_widget = Camera(play=True)
        image_layout.add_widget(self.camera_widget)

        # Captured image widget
        self.image_widget = Image(opacity=0)
        image_layout.add_widget(self.image_widget)
        layout.padding = [0, 0, 0, 40]

        # Buttons layout
        buttons_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=80, spacing=70, padding=[30, 30, 30, 30])
        layout.add_widget(buttons_layout)

        # Capture Image button
        capture_button = Button(text='Capture Image', size_hint=(0.05, None), height=40)
        capture_button.bind(on_press=self.on_capture_button_press)
        buttons_layout.add_widget(capture_button)

        # Speak Prompt button
        speak_prompt_button = Button(text='Speak Prompt', size_hint=(0.05, None), height=40)
        speak_prompt_button.bind(on_press=self.on_ask_prompt_button_press)
        buttons_layout.add_widget(speak_prompt_button)

        # Ask Gemini button
        ask_gemini_button = Button(text='Ask Gemini', size_hint=(0.05, None), height=40)
        ask_gemini_button.bind(on_press=self.on_ask_gemini_button_press)
        buttons_layout.add_widget(ask_gemini_button)

        return layout
    
    def update_rect(self, instance, value):
        # Update the position and size of the rectangle when the layout size changes
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def on_capture_button_press(self, instance):
        #if self.sound1:
        #    self.sound1.play()
        if not self.camera_access_granted:
            Logger.warning("Cannot capture image. Live feed is active.")
            return

        if self.camera_widget.texture:
            buffer = self.camera_widget.texture.pixels
            image_array = np.frombuffer(buffer, dtype=np.uint8)
            image_array = image_array.reshape((self.camera_widget.texture.height, self.camera_widget.texture.width, 4))

            # Convert RGBA to RGB
            frame = cv2.cvtColor(image_array, cv2.COLOR_RGBA2BGR)

            # Save the captured image
            cv2.imwrite('captured_image.jpg', frame)
            Logger.info("Image captured successfully!")

            # Display the captured image in the image_widget
            buf1 = cv2.flip(frame, 0)
            buf = buf1.tobytes()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.image_widget.texture = texture

            # Store the captured image
            self.captured_image = frame
            self.image_widget.opacity = 1

    def on_ask_prompt_button_press(self, instance):
        #if self.sound2:
        #    self.sound2.play()
        # Handle asking prompt using SpeechToText
        self.prompt = self.stt.listen_and_convert()
        Logger.info(f"User input: {self.prompt}")

    def on_ask_gemini_button_press(self, instance):
        #if self.sound3:
        #    self.sound3.play()
        if self.prompt and self.captured_image is not None:
            try:
                # Convert NumPy array to PIL Image
                image_pil = ig.fromarray(self.captured_image)
                contents = [self.prompt,image_pil]
                Logger.info(f"Contents before Gemini: {contents}")

                # Call the Gemini model to generate content based on the user input and captured image
                self.gemini_response = self.gemini_vision.generate_content(contents)

                # Check if the Gemini response is not empty
                if self.gemini_response and self.gemini_response.text:
                    # Convert the Gemini response to speech and play it
                    self.tts.speak(self.gemini_response.text)

                    # Log the Gemini response
                    Logger.info(f"Gemini response: {self.gemini_response.text}")
                else:
                    Logger.warning("Gemini response is empty. Please check your model or adjust the contents.")
            except Exception as e:
                Logger.error(f"Error processing user input with Gemini model: {e}")
        else:
            Logger.warning("User input or captured image is empty. Please check your microphone or camera.")

    def close_app(self, instance):
        App.get_running_app().stop()
        Window.close()        
      
if __name__ == "__main__":
    YourKivyApp().run()



