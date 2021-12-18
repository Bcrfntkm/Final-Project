from pygame.mixer import *

init(44100, -16, 2, 4096)

rocket_powerup = Sound('sound_effects/ROCKETPOWERUP.WAV')
rocket_lauch = Sound('sound_effects/ROCKETRELEASE.WAV')
explosion = Sound('sound_effects/Explosion1.wav')
rocket_fly = Sound('sound_effects/NUKEPART2.WAV')
gun_fire = Sound('sound_effects/HANDGUNFIRE.WAV')
click = Sound('sound_effects/KEYCLICK.WAV')
splash = Sound('sound_effects/Splash.wav')
team_drop = Sound('sound_effects/TeamDrop.wav')
select_worm = Sound('sound_effects/WORMSELECT.WAV')
walk_right = Sound('sound_effects/Walk-Compress.wav')
walk_left = Sound('sound_effects/Walk-Expand.wav')
impact = Sound('sound_effects/WORMIMPACT.WAV')
dead_worm = Sound('sound_effects/COUGH5.WAV')
gameover = Sound('sound_effects/GAMEOVER.WAV')