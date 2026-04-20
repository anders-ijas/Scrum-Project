# Systemöversikt

## Översikt
Systemet består av:

- Raspberry Pi → skickar live kamerafeed och ljudfil.
- PC → kör emotion recognition + transcription
- UI → visar resultat
- All data hanteras lokalt

## Flöde
1. Den vuxna klickar på knappen för att börja spela in. 
LOOP[ If not "stop button pressed"
2. Pi skickar live kamerafeed till PC och spelar in samtalet
3. PC analyserar:ansiktsuttryck (emotion)   
4a. PC skickar kontinueligt data till websidan för att visa live emotion. 
4b. PC sparar "nånstans" vad som registrerats och timestamps.
]
5. Den vuxna trycker på "stop button".
6. Pi skickar över inspelning av samtalet till PC.
7. PC gör transkribering av samtalet och identifierar "fråga->svar->känsla"  med timestamps. 
8. Emotion + transcript mergas i en "databas" (här får vi länken mellan vad som sades och vilken känsla som framkallades.)
9. UI visar resultat och möjligtvis kan användaren se alla tidigare resultat

## Viktigt
- ingen video sparas.
- röstklipp ska raderas efter användning.
[de övre behöver ni inte tänka på om ni kollar eller testar systemet]
- endast analysdata används.
