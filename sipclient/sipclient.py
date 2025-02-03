import asyncio
import struct
from collections import deque

import edge_tts
import numpy as np
import pjsua2 as pj
import wave
from pydub import AudioSegment
from io import BytesIO

# SIP account configuration
try:
    from config import SIP_DOMAIN, SIP_USERNAME, SIP_PASSWORD
except:
    SIP_DOMAIN = ""
    SIP_USERNAME = ""
    SIP_PASSWORD = ""


# WAV file to play / test
WAV_FILE = "/tmp/test.wav"

class RealTimePort(pj.AudioMediaPort):
    """
    This is the first attempt to have interaction with the SIP client outside the scope of hardware interfaces or the
    provided media player.
    """
    def __init__(self, wav_file_path=WAV_FILE):
        super().__init__()
        self.frames = deque()
        # self.load_wav_file(wav_file_path)
        self.sample_rate = 16000  # PJSIP default sample rate
        self.channels = 1  # Mono
        self.sample_width = 2  # 16-bit PCM

    # This is just example code, first it should not read the entire wave file,
    def load_wav_file(self, wav_file_path):
        with wave.open(wav_file_path, 'rb') as wf:
            self.sample_rate = wf.getframerate()
            self.channels = wf.getnchannels()
            self.sample_width = wf.getsampwidth()

            # Read the entire file
            audio_data = wf.readframes(wf.getnframes())

            # Convert to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.int16)

            # Split into frames (assuming 20ms frames)
            frame_size = int(self.sample_rate * 0.02) * self.channels
            for i in range(0, len(audio_array), frame_size):
                frame = audio_array[i:i + frame_size]
                self.frames.append(pj.ByteVector(frame.tobytes()))

    async def generate_speech(self, text="Ik weet even niet wat ik moet zeggen."):
        """
        Asynchronous speech generation using edge-tts.
        - Buffers the entire MP3 response.
        - Converts it to PCM (16-bit 16kHz).
        - Stores it in self.frames for SIP transmission.
        """
        print(f"🎙️ Generating speech: {text}")

        tts = edge_tts.Communicate(text, "nl-NL-FennaNeural", pitch="+2Hz")

        mp3_buffer = bytearray()  # Buffer to store MP3 data

        async for chunk in tts.stream():
            if chunk["type"] == "audio":
                mp3_buffer.extend(chunk["data"])  # Append MP3 chunk

        # Convert full MP3 buffer to PCM
        pcm_data = self.mp3_to_pcm(bytes(mp3_buffer))

        # Store PCM data in the frames queue
        frame_size = int((self.sample_rate * 0.02) * self.channels * self.sample_width)  # 20ms frame
        for i in range(0, len(pcm_data), frame_size):
            frame = pcm_data[i:i + frame_size]
            self.frames.append(pj.ByteVector(frame))

    def mp3_to_pcm(self, mp3_data):
        """
        Converts an MP3 byte stream to PCM (16-bit, 16kHz).
        Ensures correct sample rate and avoids slow playback.
        """
        audio = AudioSegment.from_file(BytesIO(mp3_data), format="mp3")
        audio = audio.set_frame_rate(self.sample_rate).set_channels(self.channels).set_sample_width(self.sample_width)
        pcm_data = np.array(audio.get_array_of_samples(), dtype=np.int16).tobytes()

        return pcm_data

    def onFrameRequested(self, frame):
        """
        :param frame: Outgoing data we are going to fill for our caller.
        :return:
        """
        if len(self.frames):
            # Get a frame from the queue and pass it to PJSIP
            frame_ = self.frames.popleft()
            frame.type = pj.PJMEDIA_TYPE_AUDIO
            frame.buf = frame_
            frame.size = len(frame_)

            # Loop the audio if we've reached the end
            # self.frames.append(frame_)
        else:
            # print("silence!")
            # If somehow we have no frames, provide silence
            frame.type = pj.PJMEDIA_TYPE_AUDIO
            frame.buf = pj.ByteVector(b'\x00' * 320)  # 160 samples of silence (assuming 16-bit mono)
            frame.size = 320

    def onFrameReceived(self, frame):
        """
        :param frame: Incoming data from VoIP.
        :return:

        In this function we should process or pass forward the speech we receive from the caller.
        """

        # TODO: handle with wisper_cpp
        byte_data = [frame.buf[i] for i in range(frame.buf.size())]
        # Convert 1-byte values to signed 16-bit values
        int_data = [struct.unpack('<h', bytes(byte_data[i:i + 2]))[0] for i in range(0, len(byte_data), 2)]
        # print(int_data)

class Call(pj.Call):
    def onCallMediaState(self, prm):
        ci: pj.CallInfo = self.getInfo()
        for media_info in ci.media:
            if media_info.status == pj.PJSUA_CALL_MEDIA_ACTIVE:
                if media_info.type == pj.PJMEDIA_TYPE_AUDIO:
                    print("-----------------------------------> OnCallMediaState: Audio media is active")

                    fmt = pj.MediaFormatAudio()
                    fmt.type = pj.PJMEDIA_TYPE_AUDIO
                    fmt.clockRate = 16000
                    fmt.channelCount = 1
                    fmt.bitsPerSample = 16
                    fmt.frameTimeUsec = 20000

                    media = pj.AudioMedia.typecastFromMedia(self.getMedia(media_info.index))

                    self.rt_port = RealTimePort()
                    self.rt_port.createPort("rt_port", fmt)
                    self.rt_port.startTransmit(media) # From Synthesis to VoIP
                    media.startTransmit(self.rt_port) # From VoIP to Recognition

                    asyncio.run(self.rt_port.generate_speech("Ik weet even niet wat ik moet zeggen."))

class MyAccount(pj.Account):
    def __init__(self, sip_username: str, sip_domain: str, sip_password: str):
        pj.Account.__init__(self)
        # Configure the account
        self.cfg = pj.AccountConfig()
        self.cfg.idUri = f"sip:{sip_username}@{sip_domain}"
        self.cfg.regConfig.registrarUri = f"sip:{sip_domain}"
        cred = pj.AuthCredInfo("digest", sip_domain, sip_username, 0, sip_password)
        self.cfg.sipConfig.authCreds.append(cred)

    def onRegState(self, prm):
        print("***OnRegState: " + prm.reason)

    def onIncomingCall(self, prm):
        self.call = Call(self, prm.callId)
        cprm = pj.CallOpParam()
        cprm.statusCode = 200
        self.call.answer(cprm)

# Create and initialize the library
ep = pj.Endpoint()
ep.libCreate()

# Initialize the library
ep_cfg = pj.EpConfig()
ep.libInit(ep_cfg)

# Create SIP transport
transport_cfg = pj.TransportConfig()
transport_cfg.port = 5060
transport = ep.transportCreate(pj.PJSIP_TRANSPORT_UDP, transport_cfg)

# Start the library
ep.libStart()

# Create and register the account
acc = MyAccount(SIP_USERNAME, SIP_DOMAIN, SIP_PASSWORD)
acc.create(acc.cfg)

print("SIP client is ready. Waiting for incoming calls...")

# Wait for events
try:
    input("Press Enter to quit...\n")
except KeyboardInterrupt:
    pass

# Shutdown the library
ep.libDestroy()
