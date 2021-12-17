import colors

screen_width = 1000
screen_height = 600
background_image = 'images/background.jpg'

frame_rate = 50

row_count = 6
brick_width = 60
brick_height = 20
brick_color = colors.RED1
offset_y = brick_height + 10

ball_speed = 3
ball_radius = 8
ball_color = colors.GREEN

paddle_width = 80
paddle_height = 20
paddle_color = colors.ALICEBLUE
paddle_speed = 6

status_offset_y = 5

text_color = colors.YELLOW1
initial_lives = 3
lives_right_offset = 85
lives_offset = screen_width - lives_right_offset
score_offset = 5

font_name = 'Tahoma'
font_size = 15

effect_duration = 20

sounds_effects = dict(
    brick_hit='sound_effects/brick_hit.wav',
    effect_done='sound_effects/effect_done.wav',
    paddle_hit='sound_effects/paddle_hit.wav',
    level_complete='sound_effects/level_complete.wav',
)

button_pictures = {
    'PLAY': 'images/play.png',
    'QUIT': 'images/quit.png',
    'GUN': 'images/gun.png',
    'ANOTHER GUN': 'images/bomb.png'
}
message_duration = 1

button_text_color = colors.WHITE,
button_normal_back_color  = colors.INDIANRED1
button_hover_back_color    = colors.INDIANRED2
button_pressed_back_color = colors.INDIANRED3

menu_button_w = 60
menu_button_h = 40
menu_offset_y = 20
menu_offset_x = screen_width-menu_button_w-menu_offset_y

sprite_width =20
sprite_height =20
ground_image = 'images/ground.png'
worm_image_1 = 'images/worm1.png'
worm_image_2 = 'images/worm2.png'
player_image_1 = 'images/player1.png'
player_image_2 = 'images/player2.png'
gun_image='images/G.png'
bullet_image='images/bullet.png'
gun2_image='images/B.png'
bullet2_image='images/Gr.png'

