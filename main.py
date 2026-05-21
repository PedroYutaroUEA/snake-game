import turtle
import time

DELAY = 0.1

# Screen Setup
WN = turtle.Screen()
WN.title("Snake Ganme")
WN.bgcolor("green")
WN.setup(width=600, height=600)
WN.tracer(0)  # turns off screen updates

# Snake head
head = turtle.Turtle()
head.speed(0)
head.shape("square")
head.color("black")
head.penup()
head.goto(0, 0)
head.direction = "stop"


# Functions
def go_up():
    head.direction = "up"


def go_down():
    head.direction = "down"


def go_left():
    head.direction = "left"


def go_right():
    head.direction = "right"


def move():
    if head.direction == "up":
        y = head.ycor()
        head.sety(y + 20)
    if head.direction == "down":
        y = head.ycor()
        head.sety(y - 20)
    if head.direction == "left":
        x = head.xcor()
        head.setx(x - 20)
    if head.direction == "right":
        x = head.xcor()
        head.setx(x + 20)


# Keyboard bindings
WN.listen()
WN.onkeypress(go_up, "w")
WN.onkeypress(go_down, "s")
WN.onkeypress(go_left, "a")
WN.onkeypress(go_right, "d")

# Game main loop
while True:
    WN.update()
    move()
    time.sleep(DELAY)

WN.mainloop()
