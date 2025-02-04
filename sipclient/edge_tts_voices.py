import asyncio
from edge_tts import list_voices, Communicate


async def main():
    voices = await list_voices()

    # Filter for Dutch female voices
    dutch_female_voices = [v for v in voices if v["Locale"] == "nl-NL" and v["Gender"] == "Female"]

    for voice in dutch_female_voices:
        print(f"Name: {voice['Name']}")
        print(f"Short Name: {voice['ShortName']}")
        print(f"Gender: {voice['Gender']}")
        print(f"Locale: {voice['Locale']}")

        # Render the sentence
        communicate = Communicate("Met Ailisa. Waar wil je naar toe?", voice["ShortName"], pitch="+2Hz", )

        # Generate a unique filename for each voice
        filename = f"output_{voice['ShortName']}.mp3"

        try:
            await communicate.save(filename)
            print(f"Audio saved as {filename}")
        except Exception as e:
            print(f"Error saving audio: {str(e)}")

        print("---")


asyncio.run(main())