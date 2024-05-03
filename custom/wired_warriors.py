import pygame
import sys
from pythonosc import udp_client
import math
import time

robot = 0
quadrant = "ALL" # Options Q1, Q2, Q3, Q4, ALL
ip = "192.168.1.138"
port = 55565
# ip = "127.0.0.1"
# port = 9002
client = udp_client.SimpleUDPClient(ip, port)

def send_pos(robot, joystick_x, joystick_y, joystick_z):
    address = "/motion/pos"
    x = 1-((joystick_x - min_val_x) / mean_x)
    y = 1-((joystick_y - min_val_y) / mean_y)
    z = (joystick_z - min_val_y) / mean_y
    message = [robot, x, y, z]
    client.send_message(address, message)
    print(f"Sent message: {address}/{message}")
    time.sleep(0.005)

    return x, y, z

def send_rot(robot, dot_angle):
    if dot_angle <= -6.28319 or dot_angle >= 6.28319:
        dot_angle = 0.0
    rot_angle = -dot_angle * (180 / math.pi)
    if rot_angle < 0.0:
        rot_angle = 360 + rot_angle
 
    address = "/motion/rot"
    rx = 0.0
    ry = 0.0
    rz = (rot_angle - min_val_rotz) / mean_rotz
    message = [robot, rx, ry, rz]
    client.send_message(address, message)
    #print(f"Sent message: {address}/{message}")
    time.sleep(0.005)

def send_reset():
    address = "/motion/reset"
    message = robot
    client.send_message(address, message)
    print(f"Sent message: {address}/{message}")

def send_enable(value):
    # Enable the robots
    address = "/motion/enable"
    client.send_message(address, value)
    print(f"Sent message: {address}/True")

#Make sure Robot is enabled
send_enable(True)

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gamepad Input Visualization")

# Initialize the joystick
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()

# Movement multiplier
MOVEMENT_MULTIPLIER = 2

# Define the bounding box sizes
BOUNDING_BOX_WIDTH = 200
BOUNDING_BOX_HEIGHT = BOUNDING_BOX_WIDTH*2  # Double the y-size

# Parameters
joystick_x, joystick_y, joystick_z = 0.0, -120.0, 0.0 #starting position
dot_angle = -1.57 #starting rotation
step = 60
min_val_x = -BOUNDING_BOX_WIDTH/2
max_val_x = BOUNDING_BOX_WIDTH/2
mean_x = max_val_x - min_val_x
min_val_y = -BOUNDING_BOX_HEIGHT/2 #same for z
max_val_y = BOUNDING_BOX_HEIGHT/2 #same for z
mean_y = max_val_y - min_val_y
min_val_rotz = 0
max_val_rotz = 360
mean_rotz = max_val_rotz - min_val_rotz

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.JOYBUTTONDOWN:
            if event.button == 1: # punch right B
                joystick_x += step
                address = "/motion/pos"
                x = 1-((joystick_x - min_val_x) / mean_x)
                message = [robot, x, y, z]
                client.send_message(address, message)
                time.sleep(0.5)
                joystick_x -= step
            elif event.button == 2: #punch left X
                joystick_x -= step
                address = "/motion/pos"
                x = 1-((joystick_x - min_val_x) / mean_x)
                message = [robot, x, y, z]
                client.send_message(address, message)
                time.sleep(0.5)
                joystick_x += step
            elif event.button == 3: #punch forward Y
                joystick_y += step
                address = "/motion/pos"
                y = 1-((joystick_y - min_val_y) / mean_y)
                message = [robot, x, y, z]
                client.send_message(address, message)
                time.sleep(0.5)
                joystick_y -= step
            elif event.button == 0: #punch back A
                joystick_y -= step
                address = "/motion/pos"
                y = 1-((joystick_y - min_val_y) / mean_y)
                message = [robot, x, y, z]
                client.send_message(address, message)
                time.sleep(0.5)
                joystick_y += step
            elif event.button == 4: #final combo LT
                # joystick_x, joystick_y, joystick_z = -100.0, 90.0, 80.0
                # dot_angle = 0.0
                # send_pos(0, joystick_x, joystick_y, joystick_z)
                # send_rot(0, dot_angle)
                # joystick_x, joystick_y, joystick_z = 100.0, 90.0, 80.0
                # dot_angle = 3.1415
                # send_pos(1, joystick_x, joystick_y, joystick_z)
                # send_rot(1, dot_angle)
                if robot == 0:
                    joystick_x, joystick_y, joystick_z = -100.0, 0.0, -130.0
                    dot_angle = 0.0
                else:
                    joystick_x, joystick_y, joystick_z = 100.0, 0.0, -130.0
                    dot_angle = 3.1415
            elif event.button == 5: #Start Sequence RT
                if robot == 0:
                    joystick_x, joystick_y, joystick_z = -80.0, 0.0, 0.0
                    dot_angle = 0.0
                    x, y, z = send_pos(robot, joystick_x, joystick_y, joystick_z)
                    send_rot(robot, dot_angle)
                    time.sleep(1.0)
                    joystick_x, joystick_y, joystick_z = -90.0, 90.0, 80.0
                    dot_angle = 0.35
                else:
                    joystick_x, joystick_y, joystick_z = 80.0, 0.0, 0.0
                    dot_angle = 3.1415
                    x, y, z = send_pos(robot, joystick_x, joystick_y, joystick_z)
                    send_rot(robot, dot_angle)
                    time.sleep(1.0)
                    joystick_x, joystick_y, joystick_z = 90.0, 90.0, 80.0
                    dot_angle = -3.5
            elif event.button == 8: #Left Joystick Button - Reset
                if y < 0.5:
                    if x > 0.5: 
                        joystick_x, joystick_y, joystick_z = -80.0, 0.0, 0.0
                        dot_angle = 0.0
                    elif x < 0.5: 
                        joystick_x, joystick_y, joystick_z = 80.0, 0.0, 0.0
                        dot_angle = 3.1415
                    x, y, z = send_pos(robot, joystick_x, joystick_y, joystick_z)
                    send_rot(robot, dot_angle)
                    time.sleep(1.0)
                send_reset()
                joystick_x = 0.0
                joystick_y = -120.0
                joystick_z = 0.0
                dot_angle = -1.57
                

            button_press = f"Button {event.button} pressed"
            print(button_press)  # Output to console

    # Read the values of RightThumbX and RightThumbY axes
    left_pad_x = joystick.get_axis(0)
    left_pad_y = -joystick.get_axis(1)
    right_thumb_x = joystick.get_axis(2)
    lt_z_minus = joystick.get_axis(4)
    rt_z_plus = joystick.get_axis(5)

    # Apply damping to reduce movement speed
    movement_x = left_pad_x * MOVEMENT_MULTIPLIER
    movement_y = left_pad_y * MOVEMENT_MULTIPLIER
    movement_z = (rt_z_plus - lt_z_minus) * MOVEMENT_MULTIPLIER
    check_rot = right_thumb_x * MOVEMENT_MULTIPLIER

    # If movement is small, consider it as zero
    if abs(movement_x) < 0.1:
        movement_x = 0
    if abs(movement_y) < 0.1:
        movement_y = 0
    if abs(movement_z) < 0.1:
        movement_z = 0
    if abs(check_rot) < 0.1:
        right_thumb_x = 0.0

    # Add the current movement to the total
    joystick_x += movement_x
    joystick_y += movement_y
    joystick_z += movement_z
    dot_angle += -right_thumb_x * 0.05  # Adjust the sensitivity as needed

    if quadrant == "Q1":
        joystick_x = max(min(joystick_x, 0.0), - BOUNDING_BOX_WIDTH/2)
        joystick_y = max(min(joystick_y, BOUNDING_BOX_HEIGHT/2), - 0.0)
    if quadrant == "Q2":
        joystick_x = max(min(joystick_x, BOUNDING_BOX_WIDTH/2), - 0.0)
        joystick_y = max(min(joystick_y, BOUNDING_BOX_HEIGHT/2), - 0.0)
    if quadrant == "Q3":
        joystick_x = max(min(joystick_x, 0.0), - BOUNDING_BOX_WIDTH/2)
        joystick_y = max(min(joystick_y, 0.0), -BOUNDING_BOX_HEIGHT/2)
    if quadrant == "Q4":
        joystick_x = max(min(joystick_x, BOUNDING_BOX_WIDTH/2), - 0.0)
        joystick_y = max(min(joystick_y, 0.0), -BOUNDING_BOX_HEIGHT/2)
    else:
        joystick_x = max(min(joystick_x, BOUNDING_BOX_WIDTH/2), - BOUNDING_BOX_WIDTH/2)
        joystick_y = max(min(joystick_y, BOUNDING_BOX_HEIGHT/2), -BOUNDING_BOX_HEIGHT/2)

    joystick_z = max(min(joystick_z, BOUNDING_BOX_HEIGHT/2), -BOUNDING_BOX_HEIGHT/2)

    # print(joystick_x, joystick_y, joystick_z)
    # print(dot_angle)

    # Send the position and rotation to Robot
    x, y, z = send_pos(robot, joystick_x, joystick_y, joystick_z)
    send_rot(robot, dot_angle)

    # UPDATE DRAWINGS ----------------
    # Clear the screen
    screen.fill((0, 0, 0))

    # # Render text
    # font = pygame.font.Font(None, 16)
    # text_lines = [
    # "Pad Left/Right --> X Movement",
    # "Pad Up/Down --> Y Movement",
    # "LT = Down, RT = Up --> Z Movement",
    # "Right Joystick Left/Right --> Z Rotation",
    # "Left Joystick Button --> Reset Position",
    # "X Button --> Punch Left",
    # "B Button --> Punch Right",
    # "Y Button --> Punch Up",
    # "A Button --> Punch Down",
    # "LB --> Final Punch",
    # "RB --> Start Sequence"
    # ]

    # y_offset = 10
    # for line in text_lines:
    #     text = font.render(line, True, (128, 128, 128))
    #     text_rect = text.get_rect(topleft=(10, y_offset))
    #     screen.blit(text, text_rect)
    #     y_offset += text.get_height() + 5  # Adjust the vertical spacing

    # font = pygame.font.Font(None, 25)    
    # text = font.render("Quadrants: " + quadrant, True, (128, 128, 128))
    # text_rect = text.get_rect(center=(WIDTH // 2 , 30))
    # screen.blit(text, text_rect)
    
    # font = pygame.font.Font(None, 50)
    # text = font.render("Q1", True, (64, 64, 64))
    # text_rect = text.get_rect(center=(WIDTH / 2 - BOUNDING_BOX_WIDTH / 4, HEIGHT / 2 - BOUNDING_BOX_HEIGHT / 4))
    # screen.blit(text, text_rect)
    # text = font.render("Q2", True, (64, 64, 64))
    # text_rect = text.get_rect(center=(WIDTH / 2 + BOUNDING_BOX_WIDTH / 4, HEIGHT / 2 - BOUNDING_BOX_HEIGHT / 4))
    # screen.blit(text, text_rect)
    # text = font.render("Q3", True, (64, 64, 64))
    # text_rect = text.get_rect(center=(WIDTH / 2 - BOUNDING_BOX_WIDTH / 4, HEIGHT / 2 + BOUNDING_BOX_HEIGHT / 4))
    # screen.blit(text, text_rect)
    # text = font.render("Q4", True, (64, 64, 64))
    # text_rect = text.get_rect(center=(WIDTH / 2 + BOUNDING_BOX_WIDTH / 4, HEIGHT / 2 + BOUNDING_BOX_HEIGHT / 4))
    # screen.blit(text, text_rect)

    # Calculate the position of the bounding box
    bounding_rect = pygame.Rect(WIDTH / 2 - BOUNDING_BOX_WIDTH / 2, HEIGHT / 2 - BOUNDING_BOX_HEIGHT / 2, BOUNDING_BOX_WIDTH, BOUNDING_BOX_HEIGHT)
    pygame.draw.rect(screen, (0, 0, 128), bounding_rect, 2)
    pygame.draw.line(screen, (135, 206, 250), (WIDTH / 2, HEIGHT / 2 - BOUNDING_BOX_HEIGHT / 2), (WIDTH / 2, HEIGHT / 2 + BOUNDING_BOX_HEIGHT / 2), 1)
    pygame.draw.line(screen, (135, 206, 250), (WIDTH / 2 - BOUNDING_BOX_WIDTH / 2, HEIGHT / 2), (WIDTH / 2 + BOUNDING_BOX_WIDTH / 2, HEIGHT / 2), 1)
    # Draw a aquare representing the thumbstick position
    sq_x = int(WIDTH / 2 + joystick_x)
    sq_y = int(HEIGHT / 2 - joystick_y)
    pygame.draw.rect(screen, (255, 255, 255), (sq_x - 5, sq_y - 5, 10, 10))

    # Calculate position and draw Z line and square
    pygame.draw.line(screen, (135, 206, 250), (WIDTH - WIDTH / 12, HEIGHT / 2 - BOUNDING_BOX_HEIGHT / 2), (WIDTH - WIDTH / 12, HEIGHT / 2 + BOUNDING_BOX_HEIGHT / 2), 1)
    sq2_y = int(HEIGHT / 2 - joystick_z)
    pygame.draw.rect(screen, (255, 255, 255), ((WIDTH - WIDTH / 12)-5, sq2_y - 5, 10, 10))

    # Calculate the position of the pink circle and draw it
    circle_radius = (BOUNDING_BOX_HEIGHT + 100) // 2
    circle_center = (WIDTH / 2, HEIGHT / 2)
    pygame.draw.circle(screen, (100, 149, 237), circle_center, circle_radius, 3)
    dot_x = int(circle_center[0] + circle_radius * -math.cos(dot_angle))
    dot_y = int(circle_center[1] + circle_radius * -math.sin(dot_angle))
    pygame.draw.circle(screen, (255, 255, 255), (dot_x, dot_y), 5)

    # Update the display
    pygame.display.flip()

    # Limit frame rate
    pygame.time.Clock().tick(30)  # Reduced frame rate

# Reset the robot
# send_reset()

# Disable the robots
# send_enable(False)
