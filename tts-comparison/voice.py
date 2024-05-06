import os
import wave
import pygame
import torch
from openvoice import se_extractor
from openvoice.api import ToneColorConverter
from melo.api import TTS
import piper
import subprocess
class VoiceService:
    def __init__(self) -> None:
        # self._ckpt_converter = 'modules/openvoice/checkpoints_v2/converter'
        self._device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self._output_dir = 'outputs_v2'

        # self._tone_color_converter = ToneColorConverter(f'{self._ckpt_converter}/config.json', device=self._device)
        # self._tone_color_converter.load_ckpt(f'{self._ckpt_converter}/checkpoint.pth')

        os.makedirs(self._output_dir, exist_ok=True)
    
    # def openvoice_v2(self):
    #     reference_speaker = 'modules/openvoice/resources/demo_speaker2.mp3' # This is the voice you want to clone
    #     target_se, audio_name = se_extractor.get_se(reference_speaker, self._tone_color_converter, vad=True)

    #     texts = {
    #         'EN_NEWEST': "Did you ever hear a folk tale about a giant turtle?",  # The newest English base speaker model
    #         'EN': "Did you ever hear a folk tale about a giant turtle?",
    #     }


    #     src_path = f'{self._output_dir}/tmp.wav'

    #     # Speed is adjustable
    #     speed = 1.0

    #     for language, text in texts.items():
    #         model = TTS(language=language, device=self._device, ckpt_path="modules/melo/checkpoints/checkpoint.pth", config_path="modules/melo/checkpoints/config.json")
    #         speaker_ids = model.hps.data.spk2id
            
    #         for speaker_key in speaker_ids.keys():
    #             speaker_id = speaker_ids[speaker_key]
    #             speaker_key = speaker_key.lower().replace('_', '-')
    #             print(speaker_key)
                
    #             source_se = torch.load(f'modules/openvoice/checkpoints_v2/base_speakers/ses/{speaker_key}.pth', map_location=self._device)
    #             model.tts_to_file(text, speaker_id, src_path, speed=speed)
    #             save_path = f'{self._output_dir}/output_v2_{speaker_key}_{language}.wav'

    #             # Run the tone color converter
    #             encode_message = "@MyShell"
    #             self._tone_color_converter.convert(
    #                 audio_src_path=src_path, 
    #                 src_se=source_se, 
    #                 tgt_se=target_se, 
    #                 output_path=save_path,
    #                 message=encode_message)
    #             self.play(save_path)
                
    # def openvoice(self, text):
    #     reference_speaker = 'modules/openvoice/resources/jarvis.wav' # This is the voice you want to clone
    #     target_se, audio_name = se_extractor.get_se(reference_speaker, self._tone_color_converter, vad=True)
    #     source_se = torch.load(f'modules/openvoice/checkpoints_v2/base_speakers/ses/en-newest.pth', map_location=self._device)
    #     save_path = f'{self._output_dir}/output.wav'
    #     src_path = self.melotts(text, standalone=False)
    #     # Run the tone color converter
    #     encode_message = "@MyShell"
    #     self._tone_color_converter.convert(
    #         audio_src_path=src_path, 
    #         src_se=source_se, 
    #         tgt_se=target_se, 
    #         output_path=save_path,
    #         message=encode_message)
    #     self.play(save_path)

    def pipertts_cli(self, text):
        try:
            save_path = f'{self._output_dir}/output.wav'
            command = f"""
            export DYLD_LIBRARY_PATH=`pwd`/modules/piper/pp/install/lib/ && 
            echo '{text}' |   piper --model modules/piper/models/en_US/en_US-libritts_r-medium.onnx -s 8 --length-scale 0.9 --output_file {save_path}
            """
            
            subprocess.run(command, shell=True)
            self.play(save_path)
        finally:
            print("Finished Speaking!")
            
    def pipertts(self, text):
        # Run the base speaker tts
        try:

            save_path = f'{self._output_dir}/piper2.wav'
            model_path = 'modules/piper/models/'
            model = 'en_US/en_US-libritts_r-medium.onnx'
            
            synthesize_args = {
                "speaker_id": 8,
                "length_scale": 0.9,
            }

            voice = piper.PiperVoice.load(
                model_path=model_path + model,
                config_path=model_path + model + ".json",
                use_cuda=False)

            with wave.open(str(save_path), "wb") as wav_file:
                voice.synthesize(text, wav_file, **synthesize_args)
                
            self.play(save_path)

        finally:
            print("Finished speaking!")
            
                
    def melotts(self, text, standalone=True):
        model = TTS(language="EN_NEWEST", device="cpu", ckpt_path="modules/melo/checkpoints/checkpoint.pth", config_path="modules/melo/checkpoints/config.json")
        src_path = f'{self._output_dir}/tmp.wav'

        # Speed is adjustable
        speed = 1.1
        model.tts_to_file(text, 3, src_path, speed=speed)
        return self.play(src_path) if standalone else src_path
                
    def play(self, temp_audio_file):
        
        pygame.mixer.init()
        pygame.mixer.music.load(temp_audio_file)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        pygame.mixer.music.stop()
        pygame.mixer.quit()

        # os.remove(temp_audio_file)   