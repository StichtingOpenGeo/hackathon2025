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
        communicate = Communicate("""
                                  Begin je reis te voet vanaf je huidige locatie. Je loopt ongeveer 740 meter naar Rotterdam Centraal, wat ongeveer 10 minuten duurt. Eenmaal aangekomen op Rotterdam Centraal, neem je de Intercity Direct richting Amersfoort Schothorst vanaf spoor 12. Deze trein vertrekt met een vertraging en zal om 12:46 vertrekken. De treinrit duurt ongeveer 32 minuten, waarbij je onderweg enkele haltes passeert.

Je stapt uit bij Amsterdam Zuid. Hier kom je aan op spoor 1 om 13:18. Vervolgens loop je een korte afstand van ongeveer 140 meter naar het metrostation, waar je instapt op metrolijn 52 richting Noord. Deze metro vertrekt om 13:25 en de rit duurt ongeveer 8 minuten. Je stapt uit bij de halte Rokin om 13:33.

Vanaf de halte Rokin leg je het laatste gedeelte van je reis te voet af. Dit is een wandeling van minder dan een kilometer naar je eindbestemming en duurt ongeveer 14 minuten.

Wees tijdens de reis attent op eventuele veranderingen in vertrektijden en sporen. Veel succes met je reis!
                                  """, voice["ShortName"], pitch="+2Hz", )

        # Generate a unique filename for each voice
        filename = f"output_{voice['ShortName']}.mp3"

        try:
            await communicate.save(filename)
            print(f"Audio saved as {filename}")
        except Exception as e:
            print(f"Error saving audio: {str(e)}")

        print("---")


asyncio.run(main())