import turtle
import time
import random

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

# Snake-Food
food = turtle.Turtle()
food.speed(0)
food.shape("circle")
food.color("red")
food.penup()
food.goto(0, 100)

# Snake segments
segments = []


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

    # snake VS Screen Border
    if (head.xcor() > 290 or head.xcor() < -290) or (
        head.ycor() > 290 or head.ycor() < -290
    ):
        time.sleep(1)
        head.goto(0, 0)
        head.direction = "stop"

        # hide segments
        for seg in segments:
            seg.goto(1_000, 1_000)
        segments.clear()

    # snake VS food
    if head.distance(food) < 20:
        # move food to random spot on screen
        x = random.randint(-290, 290)
        y = random.randint(-290, 290)
        food.goto(x, y)

        # add segment
        new_seg = turtle.Turtle()
        new_seg.speed(0)
        new_seg.shape("square")
        new_seg.color("grey")
        new_seg.penup()
        segments.append(new_seg)

    # Move segments from last to first
    for i in range(len(segments) - 1, 0, -1):
        x = segments[i - 1].xcor()
        y = segments[i - 1].ycor()
        segments[i].goto(x, y)

    # Move segment 0 to head
    if len(segments) > 0:
        x = head.xcor()
        y = head.ycor()
        segments[0].goto(x, y)

    move()

    time.sleep(DELAY)

WN.mainloop()
