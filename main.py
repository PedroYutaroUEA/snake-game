import turtle
import time
import random

# Constants
delay = 0.1

# Variables
score = 0
high_score = 0

# Screen Setup
WN = turtle.Screen()
WN.title("Snake Ganme - turtle")
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

# Pen
pen = turtle.Turtle()
pen.speed(0)
pen.shape("square")
pen.color("white")
pen.penup()
pen.hideturtle()
pen.goto(0, 260)
pen.write(
    f"Score: {score} | High Score: {high_score}",
    align="center",
    font=("Courier", 24, "normal"),
)


# Functions
def go_up():
    if head.direction != "down":
        head.direction = "up"


def go_down():
    if head.direction != "up":
        head.direction = "down"


def go_left():
    if head.direction != "right":
        head.direction = "left"


def go_right():
    if head.direction != "left":
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

    # --- COLLISION: snake VS Screen Border
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

        # --- RESET Game State
        delay = 0.1
        score = 0
        pen.clear()
        pen.write(
            f"Score: {score} | High Score: {high_score}",
            align="center",
            font=("Courier", 24, "normal"),
        )

    # --- COLLISION: snake VS food
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

        # shorten the delay
        delay -= 0.001

        # increase score
        score += 10
        if score > high_score:
            high_score = score

        pen.clear()
        pen.write(
            f"Score: {score} | High Score: {high_score}",
            align="center",
            font=("Courier", 24, "normal"),
        )

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

    # --- COLLISION: snake VS segments
    for seg in segments:
        if seg.distance(head) < 20:
            time.sleep(1)
            head.goto(0, 0)
            head.direction = "stop"

            # hide segments
            for seg in segments:
                seg.goto(1_000, 1_000)
            segments.clear()

            # --- RESET Game State
            delay = 0.1
            score = 0
            pen.clear()
            pen.write(
                f"Score: {score} | High Score: {high_score}",
                align="center",
                font=("Courier", 24, "normal"),
            )

    time.sleep(delay)

WN.mainloop()
